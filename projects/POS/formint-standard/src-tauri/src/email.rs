use diesel::prelude::*;
use lettre::message::header::ContentType;
use lettre::message::Mailbox;
use lettre::transport::smtp::authentication::Credentials;
use lettre::{Message, SmtpTransport, Transport};
use std::env;
use std::path::PathBuf;

// Load email template from file
fn load_email_template() -> Result<String, String> {
    let template = include_str!("../templates/support_email.html");
    Ok(template.to_string())
}

/// SMTP configuration resolved from the settings DB (with env fallback).
/// Precedence: settings DB (row 1) → environment variables → defaults.
#[derive(Debug, Clone)]
pub struct SmtpConfig {
    pub server: String,
    pub port: u16,
    pub username: String,
    pub password: String,
    pub recipient: String,
    pub from_name: String,
    pub from_email: String,
}

impl SmtpConfig {
    /// Whether credentials are fully configured (username + password present).
    pub fn is_configured(&self) -> bool {
        !self.username.trim().is_empty() && !self.password.trim().is_empty()
    }

    /// Whether a recipient (support inbox) is configured.
    pub fn has_recipient(&self) -> bool {
        !self.recipient.trim().is_empty()
    }
}

/// Load SMTP configuration from the settings DB, falling back to env vars.
///
/// Implementation: start from env vars / built-in defaults, then override
/// each field with the settings.smtp_* column (set via Settings → Email) when
/// the DB value is non-empty. Effective priority per field:
///   1. settings.smtp_* column
///   2. SMTP_* environment variable (legacy .env support)
///   3. built-in default
pub fn load_smtp_config(db_path: &PathBuf) -> SmtpConfig {
    // ── Defaults (env first, then hardcoded) ──
    let server = env::var("SMTP_SERVER").unwrap_or_else(|_| "smtp.gmail.com".to_string());
    let port = env::var("SMTP_PORT")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(587);
    let username = env::var("SMTP_USERNAME").unwrap_or_default();
    let password = env::var("SMTP_PASSWORD").unwrap_or_default();
    let recipient = env::var("SMTP_RECIPIENT").unwrap_or_default();
    let from_name = env::var("SMTP_FROM_NAME").unwrap_or_else(|_| "Formint".to_string());
    let from_email = env::var("SMTP_FROM_EMAIL").unwrap_or_default();

    let mut cfg = SmtpConfig {
        server,
        port,
        username,
        password,
        recipient,
        from_name,
        from_email,
    };

    // ── Override from settings DB (row 1) if present ──
    if let Ok(mut conn) = crate::db::open_conn(db_path) {
        use crate::db::schema::settings::dsl::*;
        if let Ok(s) = settings.find(1).first::<crate::db::models::Settings>(&mut conn) {
            if let Some(v) = s.smtp_server {
                if !v.trim().is_empty() {
                    cfg.server = v;
                }
            }
            if let Some(v) = s.smtp_port {
                if v > 0 {
                    cfg.port = v as u16;
                }
            }
            if let Some(v) = s.smtp_username {
                if !v.trim().is_empty() {
                    cfg.username = v;
                }
            }
            if let Some(v) = s.smtp_password {
                if !v.trim().is_empty() {
                    cfg.password = v;
                }
            }
            if let Some(v) = s.smtp_recipient {
                if !v.trim().is_empty() {
                    cfg.recipient = v;
                }
            }
            if let Some(v) = s.smtp_from_name {
                if !v.trim().is_empty() {
                    cfg.from_name = v;
                }
            }
            if let Some(v) = s.smtp_from_email {
                if !v.trim().is_empty() {
                    cfg.from_email = v;
                }
            }
        }
    }

    // Derive from_email from username if not explicitly set
    if cfg.from_email.trim().is_empty() && !cfg.username.trim().is_empty() {
        cfg.from_email = cfg.username.clone();
    }

    cfg
}

/// Resolve the display "from" address for outgoing mail.
fn resolve_from_address(cfg: &SmtpConfig) -> Result<lettre::Address, String> {
    let addr = cfg
        .from_email
        .parse::<lettre::Address>()
        .map_err(|e| format!("Invalid SMTP from email '{}': {}", cfg.from_email, e))?;
    Ok(addr)
}

pub fn send_confirmation_email(db_path: &PathBuf, recipient: &str, code: &str) -> Result<(), String> {
    let cfg = load_smtp_config(db_path);
    if !cfg.is_configured() {
        return Err("SMTP not configured. Configure it in Settings → Email.".to_string());
    }

    let email_body = format!(
        "<html><body style=\"font-family: Arial, sans-serif; padding: 20px;\">
            <h2>Email Confirmation</h2>
            <p>Your confirmation code is:</p>
            <h1 style=\"font-size: 32px; letter-spacing: 5px; color: #0d9488;\">{}</h1>
            <p>This code will expire in 5 minutes.</p>
            <p>If you did not request this, please ignore this email.</p>
        </body></html>",
        code
    );

    let from = resolve_from_address(&cfg)?;
    let email_message = lettre::Message::builder()
        .from(Mailbox::new(Some(cfg.from_name.clone()), from))
        .to(recipient.parse().map_err(|e| format!("Invalid recipient address: {}", e))?)
        .subject("Formint: Email Confirmation Code")
        .header(lettre::message::header::ContentType::TEXT_HTML)
        .body(email_body)
        .map_err(|e| format!("Failed to build email: {}", e))?;

    send_with_config(&cfg, email_message)
}

pub fn send_support_email(
    db_path: &PathBuf,
    name: String,
    email: String,
    subject: String,
    message: String,
) -> Result<(), String> {
    let cfg = load_smtp_config(db_path);
    if !cfg.is_configured() {
        return Err("SMTP not configured. Configure it in Settings → Email.".to_string());
    }
    if !cfg.has_recipient() {
        return Err(
            "SMTP_RECIPIENT not configured. Set the support inbox in Settings → Email.".to_string(),
        );
    }

    // Load and populate email template
    let template = load_email_template()?;
    let email_body = template
        .replace("{{SENDER_NAME}}", &name)
        .replace("{{SENDER_EMAIL}}", &email)
        .replace("{{SUBJECT}}", &subject)
        .replace("{{MESSAGE}}", &message);

    let from = resolve_from_address(&cfg)?;
    let email_message = Message::builder()
        .from(Mailbox::new(Some(cfg.from_name.clone()), from))
        .reply_to(
            email
                .parse()
                .map_err(|e| format!("Failed to parse reply-to address: {}", e))?,
        )
        .to(cfg.recipient.parse().map_err(|e| format!("Failed to parse recipient address: {}", e))?)
        .subject(format!("Support: {}", subject))
        .header(ContentType::TEXT_HTML)
        .body(email_body)
        .map_err(|e| format!("Failed to build email: {}", e))?;

    send_with_config(&cfg, email_message)
}

/// Send a support ticket email with the full contact/ticket metadata
/// (phone, category, priority, status) rendered in the email template.
/// Used by the chat widget's pre-chat form (submit_support_message).
pub fn send_support_ticket_email(
    db_path: &PathBuf,
    name: String,
    email: String,
    phone: Option<String>,
    category: Option<String>,
    priority: String,
    subject: String,
    message: String,
    status: String,
) -> Result<(), String> {
    let cfg = load_smtp_config(db_path);
    if !cfg.is_configured() {
        return Err("SMTP not configured. Configure it in Settings → Email.".to_string());
    }
    if !cfg.has_recipient() {
        return Err(
            "SMTP_RECIPIENT not configured. Set the support inbox in Settings → Email.".to_string(),
        );
    }

    // Load and populate email template
    let template = load_email_template()?;
    let email_body = template
        .replace("{{SENDER_NAME}}", &name)
        .replace("{{SENDER_EMAIL}}", &email)
        .replace("{{SUBJECT}}", &subject)
        .replace("{{MESSAGE}}", &message)
        .replace("{{CATEGORY}}", category.as_deref().unwrap_or("General"))
        .replace("{{PRIORITY}}", &priority)
        .replace("{{PHONE}}", phone.as_deref().unwrap_or("—"))
        .replace("{{STATUS}}", &status);

    let from = resolve_from_address(&cfg)?;
    let email_message = Message::builder()
        .from(Mailbox::new(Some(cfg.from_name.clone()), from))
        .reply_to(
            email
                .parse()
                .map_err(|e| format!("Failed to parse reply-to address: {}", e))?,
        )
        .to(cfg.recipient.parse().map_err(|e| format!("Failed to parse recipient address: {}", e))?)
        .subject(format!("Support: {} — [{}]", subject, priority))
        .header(ContentType::TEXT_HTML)
        .body(email_body)
        .map_err(|e| format!("Failed to build email: {}", e))?;

    send_with_config(&cfg, email_message)
}

/// Build the SMTP transport from the resolved config and send the message.
///
/// Uses STARTTLS (lettre `relay`) on the configured port (default 587).
/// Port 465 (implicit TLS) is not supported by `relay` — users should use
/// STARTTLS ports (587) for gmail and most providers.
fn send_with_config(cfg: &SmtpConfig, email_message: Message) -> Result<(), String> {
    let creds = Credentials::new(cfg.username.clone(), cfg.password.clone());

    let mailer = SmtpTransport::relay(&cfg.server)
        .map_err(|e| format!("Failed to create SMTP transport: {}", e))?
        .port(cfg.port)
        .credentials(creds)
        .build();

    mailer
        .send(&email_message)
        .map_err(|e| format!("Failed to send email: {}", e))?;

    Ok(())
}

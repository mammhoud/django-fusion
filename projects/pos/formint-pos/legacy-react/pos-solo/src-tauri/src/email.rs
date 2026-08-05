use lettre::message::header::ContentType;
use lettre::transport::smtp::authentication::Credentials;
use lettre::{Message, SmtpTransport, Transport};
use std::env;

// Load email template from file
fn load_email_template() -> Result<String, String> {
    let template = include_str!("../templates/support_email.html");
    Ok(template.to_string())
}

pub fn send_confirmation_email(recipient: &str, code: &str) -> Result<(), String> {
    let smtp_server = env::var("SMTP_SERVER").unwrap_or_else(|_| "smtp.gmail.com".to_string());
    let smtp_username = env::var("SMTP_USERNAME").map_err(|_| {
        "SMTP not configured.".to_string()
    })?;
    let smtp_password = env::var("SMTP_PASSWORD").map_err(|_| {
        "SMTP_PASSWORD not configured.".to_string()
    })?;

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

    let email_message = lettre::Message::builder()
        .from(format!("POS KO <{}>", smtp_username).parse().map_err(|e| format!("{}", e))?)
        .to(recipient.parse().map_err(|e| format!("{}", e))?)
        .subject("POS KO: Email Confirmation Code")
        .header(lettre::message::header::ContentType::TEXT_HTML)
        .body(email_body)
        .map_err(|e| format!("Failed to build email: {}", e))?;

    let creds = lettre::transport::smtp::authentication::Credentials::new(smtp_username, smtp_password);
    let mailer = lettre::SmtpTransport::relay(&smtp_server)
        .map_err(|e| format!("Failed to create SMTP transport: {}", e))?
        .credentials(creds)
        .build();

    mailer.send(&email_message)
        .map_err(|e| format!("Failed to send email: {}", e))?;

    Ok(())
}

pub fn send_support_email(
    name: String,
    email: String,
    subject: String,
    message: String,
) -> Result<(), String> {
    // Load environment variables
    let smtp_server = env::var("SMTP_SERVER").unwrap_or_else(|_| "smtp.gmail.com".to_string());
    let smtp_username = env::var("SMTP_USERNAME").map_err(|_| {
        "SMTP not configured. Please set SMTP_USERNAME environment variable.\n".to_string()
    })?;
    
    let smtp_password = env::var("SMTP_PASSWORD").map_err(|_| {
        "SMTP_PASSWORD not configured. Please set the SMTP_PASSWORD environment variable.\n\
        See SMTP_SETUP.md for instructions.".to_string()
    })?;
    
    let recipient_email = env::var("SMTP_RECIPIENT").map_err(|_| {
        "SMTP_RECIPIENT not configured. Please set the SMTP_RECIPIENT environment variable.\n".to_string()
    })?;

    // Load and populate email template
    let template = load_email_template()?;
    let email_body = template
        .replace("{{SENDER_NAME}}", &name)
        .replace("{{SENDER_EMAIL}}", &email)
        .replace("{{SUBJECT}}", &subject)
        .replace("{{MESSAGE}}", &message);

    // Build the email
    let email_message = Message::builder()
        .from(
            format!("{} <{}>", name, smtp_username)
                .parse()
                .map_err(|e| format!("Failed to parse from address: {}", e))?,
        )
        .reply_to(
            email
                .parse()
                .map_err(|e| format!("Failed to parse reply-to address: {}", e))?,
        )
        .to(recipient_email
            .parse()
            .map_err(|e| format!("Failed to parse recipient address: {}", e))?)
        .subject(format!("Support: {}", subject))
        .header(ContentType::TEXT_HTML)
        .body(email_body)
        .map_err(|e| format!("Failed to build email: {}", e))?;

    // Create SMTP credentials
    let creds = Credentials::new(smtp_username, smtp_password);

    // Create SMTP transport
    let mailer = SmtpTransport::relay(&smtp_server)
        .map_err(|e| format!("Failed to create SMTP transport: {}", e))?
        .credentials(creds)
        .build();

    // Send the email
    mailer
        .send(&email_message)
        .map_err(|e| format!("Failed to send email: {}", e))?;

    Ok(())
}


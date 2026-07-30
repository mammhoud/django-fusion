import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { invoke } from '@tauri-apps/api/core';
import { open } from '@tauri-apps/plugin-dialog';
import { readFile } from '@tauri-apps/plugin-fs';
import packageJson from '../../../package.json';
import BackButton from '../../components/layout/BackButton';
import Card from '../../components/layout/Card';
import PageLayout from '../../components/layout/PageLayout';
import { useTranslation } from 'react-i18next';
import AnimatePresence from '../../components/utils/AnimatePresence';

interface SupportMessage {
  name: string;
  email: string;
  subject: string;
  message: string;
}

interface Attachment {
  name: string;
  data: string;
  type: string;
}

interface FormErrors {
  name?: string;
  email?: string;
  subject?: string;
  message?: string;
}

export default function About() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [isNavigating, setIsNavigating] = useState(false);

  const [supportForm, setSupportForm] = useState<SupportMessage>({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [formErrors, setFormErrors] = useState<FormErrors>({});
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [userCount, setUserCount] = useState<number | null>(null);

  useEffect(() => {
    invoke<number>('get_user_count')
      .then(setUserCount)
      .catch(() => setUserCount(null));
  }, []);

  const handleBackNavigation = () => {
    setIsNavigating(true);
    setTimeout(() => {
      navigate('/dashboard');
    }, 300);
  };

  const handleSupportChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setSupportForm(prev => ({ ...prev, [name]: value }));
    if (formErrors[name as keyof FormErrors]) {
      setFormErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const validateSupportForm = (): boolean => {
    const newErrors: FormErrors = {};
    if (!supportForm.name.trim()) newErrors.name = t('support.validationName');
    if (!supportForm.email.trim()) {
      newErrors.email = t('support.validationEmail');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(supportForm.email)) {
      newErrors.email = t('support.validationEmailValid');
    }
    if (!supportForm.subject.trim()) newErrors.subject = t('support.validationSubject');
    if (!supportForm.message.trim()) {
      newErrors.message = t('support.validationMessage');
    } else if (supportForm.message.trim().length < 10) {
      newErrors.message = t('support.validationMessageLength');
    }
    setFormErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSupportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateSupportForm()) return;
    setIsSubmitting(true);
    setSubmitStatus('idle');
    setErrorMessage('');
    try {
      await invoke('send_support_email', {
        name: supportForm.name,
        email: supportForm.email,
        subject: supportForm.subject,
        message: supportForm.message
      });
      setSubmitStatus('success');
      setSupportForm({ name: '', email: '', subject: '', message: '' });
      setAttachments([]);
      setFormErrors({});
      setTimeout(() => setSubmitStatus('idle'), 5000);
    } catch (error) {
      console.error('Error sending message:', error);
      setSubmitStatus('error');
      setErrorMessage(error instanceof Error ? error.message : String(error));
      setTimeout(() => setSubmitStatus('idle'), 5000);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PageLayout
      background="bg-linear-to-br from-slate-100 via-purple-100 to-slate-100 dark:from-slate-900 dark:via-purple-900 dark:to-slate-900"
      padding="py-16 md:py-20"
    >
        {/* Header */}
        <div
          className="text-center mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className="bg-base-100/20 backdrop-blur-sm rounded-full p-6 w-fit mx-auto mb-6"
          >
            <span className="icon-[tabler--heart] w-16 h-16 md:w-20 md:h-20 text-teal-500 dark:text-teal-400" />
          </div>
          <h1
            className="text-3xl md:text-5xl font-bold text-transparent bg-clip-text
              bg-linear-to-r from-teal-600 to-purple-600 dark:from-teal-400 dark:to-purple-400 py-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {t('about.title')}
          </h1>
          <p className="text-base-content/70 mt-4 text-lg transition-colors duration-300">
            {t('about.subtitle')}
          </p>
        </div>

        {/* Main Content */}
        <div
          className="max-w-4xl mx-auto space-y-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {/* Project Info */}
          <Card padding="xl" transitional className="md:p-8">
            <h2 className="text-2xl font-semibold text-base-content mb-4 flex items-center gap-2">
              <span className="icon-[tabler--code] text-primary" />
              {t('about.projectTitle')}
            </h2>
            <p className="text-base-content/70 leading-relaxed mb-4">
              {t('about.projectDesc1')}
            </p>
            <p className="text-base-content/70 leading-relaxed">
              {t('about.projectDesc2')}
            </p>
          </Card>

          {/* Support & Contact */}
          <Card padding="xl" transitional className="md:p-8">
            <h2 className="text-2xl font-semibold text-base-content mb-6 flex items-center gap-2">
              <span className="icon-[tabler--mail] text-primary" />
              {t('about.supportTitle')}
            </h2>
            <p className="text-base-content/70 mb-6">
              {t('about.supportDesc')}
            </p>

            <form onSubmit={handleSupportSubmit} className="space-y-5">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-base-content/80 mb-1.5 text-sm font-medium">{t('about.supportName')}</label>
                  <input
                    type="text"
                    name="name"
                    value={supportForm.name}
                    onChange={handleSupportChange}
                    className={`input input-bordered w-full ${
                        formErrors.name
                          ? 'input-error'
                          : ''
                      }`}
                    disabled={isSubmitting}
                    placeholder={t('support.namePlaceholder')}
                  />
                  {formErrors.name && <p className="text-red-400 text-sm mt-1">{formErrors.name}</p>}
                </div>
                <div>
                  <label className="block text-base-content/80 mb-1.5 text-sm font-medium">{t('about.supportEmail')}</label>
                  <input
                    type="email"
                    name="email"
                    value={supportForm.email}
                    onChange={handleSupportChange}
                    className={`input input-bordered w-full ${
                        formErrors.email
                          ? 'input-error'
                          : ''
                      }`}
                    disabled={isSubmitting}
                    placeholder={t('support.emailPlaceholder')}
                  />
                  {formErrors.email && <p className="text-red-400 text-sm mt-1">{formErrors.email}</p>}
                </div>
              </div>

              <div>
                <label className="block text-base-content/80 mb-1.5 text-sm font-medium">{t('about.supportSubject')}</label>
                <input
                  type="text"
                  name="subject"
                  value={supportForm.subject}
                  onChange={handleSupportChange}                    className={`input input-bordered w-full ${
                        formErrors.subject
                          ? 'input-error'
                          : ''
                      }`}
                  disabled={isSubmitting}
                  placeholder={t('support.subjectPlaceholder')}
                />
                {formErrors.subject && <p className="text-red-400 text-sm mt-1">{formErrors.subject}</p>}
              </div>

              {/* ── Attachment area ── */}
              <div>
                <label className="block text-base-content/80 mb-1.5 text-sm font-medium">
                  <span className="icon-[tabler--paperclip] inline mr-1.5 w-3.5 h-3.5" />
                  {t('about.attachments') || 'Attachments'}
                </label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {attachments.map((att, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg
                        bg-white/50 dark:bg-white/10 border border-base-300/30
                        text-xs text-slate-700 dark:text-slate-300"
                    >
                      <span className="icon-[tabler--file] w-3.5 h-3.5 text-primary" />
                      <span className="max-w-[120px] truncate">{att.name}</span>
                      <button
                        type="button"
                        onClick={() => setAttachments(prev => prev.filter((_, i) => i !== idx))}
                        className="text-slate-400 hover:text-error transition-colors"
                      >
                        <span className="icon-[tabler--x] w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={async () => {
                      setIsUploading(true);
                      try {
                        const file = await open({
                          multiple: false,
                          filters: [
                            { name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'] },
                            { name: 'Documents', extensions: ['pdf', 'doc', 'docx', 'txt', 'csv', 'xls', 'xlsx'] },
                            { name: 'All Files', extensions: ['*'] },
                          ],
                          title: 'Attach file to support request',
                        });
                        if (file && typeof file === 'string') {
                          const contents = await readFile(file);
                          let binary = '';
                          const chunkSize = 8192;
                          for (let i = 0; i < contents.length; i += chunkSize) {
                            const chunk = contents.slice(i, Math.min(i + chunkSize, contents.length));
                            binary += String.fromCharCode.apply(null, Array.from(chunk));
                          }
                          const base64 = btoa(binary);
                          const fileName = file.split('/').pop() || file.split('\\').pop() || 'attachment';
                          const ext = fileName.split('.').pop()?.toLowerCase() || 'bin';
                          setAttachments(prev => [...prev, { name: fileName, data: base64, type: ext }]);
                        }
                      } catch (error) {
                        console.error('Error attaching file:', error);
                      } finally {
                        setIsUploading(false);
                      }
                    }}
                    disabled={isUploading}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium
                      bg-white/50 dark:bg-white/10 border border-base-300/30
                      text-slate-600 dark:text-slate-300 hover:bg-base-200/50
                      transition-colors flex items-center gap-1.5 disabled:opacity-50"
                  >
                    {isUploading ? (
                      <div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        className="w-3.5 h-3.5 border-2 border-primary border-t-transparent rounded-full"
                      />
                    ) : (
                      <span className="icon-[tabler--paperclip] w-3.5 h-3.5" />
                    )}
                    {t('about.attachFile') || 'Attach File'}
                  </button>
                  <button
                    type="button"
                    onClick={async () => {
                      try {
                        // Forward recent report data as context
                        const analytics = await invoke<any>('get_analytics').catch(() => null);
                        const reportRef = analytics
                          ? `\n\n--- Forwarded Report ---\n` +
                            `Total Orders: ${analytics.summary?.total_orders || 'N/A'}\n` +
                            `Total Revenue: ${analytics.summary?.total_revenue || 'N/A'}\n` +
                            `Average Order: ${analytics.summary?.average_order_value || 'N/A'}`
                          : '';
                        setSupportForm(prev => ({
                          ...prev,
                          message: prev.message + reportRef,
                        }));
                      } catch {
                        // Silently fail
                      }
                    }}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium
                      bg-white/50 dark:bg-white/10 border border-base-300/30
                      text-slate-600 dark:text-slate-300 hover:bg-base-200/50
                      transition-colors flex items-center gap-1.5"
                  >
                    <span className="icon-[tabler--chart-bar] w-3.5 h-3.5" />
                    {t('about.forwardReport') || 'Forward Report'}
                  </button>
                </div>
                {attachments.length > 0 && (
                  <p className="text-[10px] text-slate-400 mt-1">
                    {attachments.length} file(s) attached. They will be included as base64 in the email.
                  </p>
                )}
              </div>

              <button
                type="submit"
                className="btn btn-primary w-full bg-linear-to-r from-teal-400 to-purple-400 border-0 gap-2 active:scale-[0.98] transition-all"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                    />
                    {t('about.sending')}
                  </>
                ) : (
                  <>
                    <span className="icon-[tabler--send] text-lg" />
                    {t('about.sendMessage')}
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 pt-6 border-t border-base-300/30">
              <p className="text-sm text-base-content/50">
                <strong className="text-base-content/80">{t('about.otherWays')}</strong>
              </p>
              <div className="mt-3 space-y-2 text-sm text-base-content/70">
                <p>
                  🌐 {t('about.visitWebsite')}{' '}
                  <a
                    href="https://structa.cloud"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400! hover:text-purple-400! underline! transition-colors font-semibold"
                  >
                    {t('about.officialWebsite')}
                  </a>
                </p>
              </div>
            </div>
          </Card>

          {/* Version & Stats Info */}
          <Card padding="xl" center transitional className="md:p-8">
            <p className="text-base-content/70">
              <strong className="text-base-content">{t('about.versionLabel')}:</strong> {packageJson.version}
            </p>
            {userCount !== null && (
              <p className="text-base-content/70 mt-2">
                <strong className="text-base-content">{t('about.registeredUsers')}:</strong> {userCount}
              </p>
            )}
            <p className="text-base-content/50 text-sm mt-2">
              {t('about.copyright', { year: new Date().getFullYear() })}
            </p>
          </Card>

          {/* Developed by mammhoud */}
          <div
            className="text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <div className="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-3 text-base-content/70">
              <span className="text-sm">{t('about.developedBy')}</span>
              <Card radius="lg" className="flex items-center gap-2 px-4 py-2">
                <span className="text-base-content font-semibold text-lg">Structa Cloud</span>
              </Card>
            </div>
          </div>

          {/* Back Button */}
          <div className="flex justify-center">
            <BackButton onClick={handleBackNavigation} disabled={isNavigating} text={t('common.backToHome')} />
          </div>
        </div>

      {/* Success Toast */}
      <AnimatePresence>
        {submitStatus === 'success' && (
          <div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 alert alert-success shadow-lg"
          >
            <span className="icon-[tabler--check] text-xl" />
            {t('about.successToast')}
          </div>
        )}

        {submitStatus === 'error' && (
          <div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 alert alert-error max-w-md shadow-lg"
          >
            <span className="icon-[tabler--alert-triangle] text-xl" />
            <span>{errorMessage}</span>
          </div>
        )}
      </AnimatePresence>
    </PageLayout>
  );
}



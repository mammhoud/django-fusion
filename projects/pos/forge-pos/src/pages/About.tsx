import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaCode, FaHeart, FaEnvelope, FaPaperPlane, FaCheck, FaExclamationTriangle } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import { invoke } from '@tauri-apps/api/core';
import packageJson from '../../package.json';
import BackButton from '../components/BackButton';
import PageLayout from '../components/PageLayout';
import { useTranslation } from 'react-i18next';

interface SupportMessage {
  name: string;
  email: string;
  subject: string;
  message: string;
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
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const handleBackNavigation = () => {
    setIsNavigating(true);
    setTimeout(() => {
      navigate('/');
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
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className="bg-white/20 dark:bg-white/10 backdrop-blur-sm rounded-full p-6 w-fit mx-auto mb-6"
          >
            <FaHeart className="w-16 h-16 md:w-20 md:h-20 text-teal-500 dark:text-teal-400" />
          </motion.div>
          <motion.h1
            className="text-3xl md:text-5xl font-bold text-transparent bg-clip-text 
              bg-linear-to-r from-teal-600 to-purple-600 dark:from-teal-400 dark:to-purple-400 py-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {t('about.title')}
          </motion.h1>
          <p className="text-slate-600 dark:text-gray-300 mt-4 text-lg transition-colors duration-300">
            {t('about.subtitle')}
          </p>
        </motion.div>

        {/* Main Content */}
        <motion.div
          className="max-w-4xl mx-auto space-y-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {/* Project Info */}
          <div className="card--glass rounded-2xl p-6 md:p-8 transition-colors duration-300">
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
              <FaCode className="text-teal-600 dark:text-teal-400" />
              {t('about.projectTitle')}
            </h2>
            <p className="text-slate-600 dark:text-gray-300 leading-relaxed mb-4">
              {t('about.projectDesc1')}
            </p>
            <p className="text-slate-600 dark:text-gray-300 leading-relaxed">
              {t('about.projectDesc2')}
            </p>
          </div>

          {/* Support & Contact */}
          <div className="card--glass rounded-2xl p-6 md:p-8 transition-colors duration-300">
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
              <FaEnvelope className="text-teal-600 dark:text-teal-400" />
              {t('about.supportTitle')}
            </h2>
            <p className="text-slate-600 dark:text-gray-300 mb-6">
              {t('about.supportDesc')}
            </p>

            <form onSubmit={handleSupportSubmit} className="space-y-5">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label className="block text-slate-700 dark:text-gray-300 mb-1.5 text-sm font-medium">{t('about.supportName')}</label>
                  <input
                    type="text"
                    name="name"
                    value={supportForm.name}
                    onChange={handleSupportChange}
                    className={`w-full px-4 py-2.5 rounded-lg bg-white/50 dark:bg-white/5 border 
                      text-slate-900 dark:text-white focus:outline-none transition-colors ${
                        formErrors.name 
                          ? 'border-red-500 focus:border-red-400' 
                          : 'border-slate-300 dark:border-gray-600 focus:border-teal-400'
                      }`}
                    disabled={isSubmitting}
                    placeholder={t('support.namePlaceholder')}
                  />
                  {formErrors.name && <p className="text-red-400 text-sm mt-1">{formErrors.name}</p>}
                </div>
                <div>
                  <label className="block text-slate-700 dark:text-gray-300 mb-1.5 text-sm font-medium">{t('about.supportEmail')}</label>
                  <input
                    type="email"
                    name="email"
                    value={supportForm.email}
                    onChange={handleSupportChange}
                    className={`w-full px-4 py-2.5 rounded-lg bg-white/50 dark:bg-white/5 border 
                      text-slate-900 dark:text-white focus:outline-none transition-colors ${
                        formErrors.email 
                          ? 'border-red-500 focus:border-red-400' 
                          : 'border-slate-300 dark:border-gray-600 focus:border-teal-400'
                      }`}
                    disabled={isSubmitting}
                    placeholder={t('support.emailPlaceholder')}
                  />
                  {formErrors.email && <p className="text-red-400 text-sm mt-1">{formErrors.email}</p>}
                </div>
              </div>

              <div>
                <label className="block text-slate-700 dark:text-gray-300 mb-1.5 text-sm font-medium">{t('about.supportSubject')}</label>
                <input
                  type="text"
                  name="subject"
                  value={supportForm.subject}
                  onChange={handleSupportChange}
                  className={`w-full px-4 py-2.5 rounded-lg bg-white/50 dark:bg-white/5 border 
                    text-slate-900 dark:text-white focus:outline-none transition-colors ${
                      formErrors.subject 
                        ? 'border-red-500 focus:border-red-400' 
                        : 'border-slate-300 dark:border-gray-600 focus:border-teal-400'
                    }`}
                  disabled={isSubmitting}
                  placeholder={t('support.subjectPlaceholder')}
                />
                {formErrors.subject && <p className="text-red-400 text-sm mt-1">{formErrors.subject}</p>}
              </div>

              <div>
                <label className="block text-slate-700 dark:text-gray-300 mb-1.5 text-sm font-medium">{t('about.supportMessage')}</label>
                <textarea
                  name="message"
                  value={supportForm.message}
                  onChange={handleSupportChange}
                  rows={6}
                  className={`w-full px-4 py-2.5 rounded-lg bg-white/50 dark:bg-white/5 border 
                    text-slate-900 dark:text-white focus:outline-none transition-colors resize-none 
                    placeholder:text-slate-400 dark:placeholder:text-gray-400 ${
                      formErrors.message 
                        ? 'border-red-500 focus:border-red-400' 
                        : 'border-slate-300 dark:border-gray-600 focus:border-teal-400'
                    }`}
                  disabled={isSubmitting}
                  placeholder={t('support.messagePlaceholder')}
                />
                {formErrors.message && <p className="text-red-400 text-sm mt-1">{formErrors.message}</p>}
              </div>

              <motion.button
                type="submit"
                className="w-full py-3 bg-linear-to-r from-teal-400 to-purple-400 text-white rounded-xl 
                  font-semibold transition-all duration-200 flex items-center justify-center gap-2
                  disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                    />
                    {t('about.sending')}
                  </>
                ) : (
                  <>
                    <FaPaperPlane className="text-lg" />
                    {t('about.sendMessage')}
                  </>
                )}
              </motion.button>
            </form>

            <div className="mt-6 pt-6 border-t border-slate-200 dark:border-white/10">
              <p className="text-sm text-slate-500 dark:text-gray-400">
                <strong className="text-slate-700 dark:text-gray-300">{t('about.otherWays')}</strong>
              </p>
              <div className="mt-3 space-y-2 text-sm text-slate-600 dark:text-gray-300">
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
          </div>

          {/* Version Info */}
          <div className="card--glass rounded-2xl p-6 md:p-8 text-center transition-colors duration-300">
            <p className="text-slate-600 dark:text-gray-300">
              <strong className="text-slate-900 dark:text-white">{t('about.versionLabel')}:</strong> {packageJson.version}
            </p>
            <p className="text-slate-500 dark:text-gray-400 text-sm mt-2">
              {t('about.copyright', { year: new Date().getFullYear() })}
            </p>
          </div>

          {/* Developed by mammhoud */}
          <motion.div
            className="text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <div className="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-3 text-slate-600 dark:text-gray-300">
              <span className="text-sm">{t('about.developedBy')}</span>
              <div className="flex items-center gap-2 card--glass rounded-lg px-4 py-2 transition-colors duration-300">
                <span className="text-slate-900 dark:text-white font-semibold text-lg">Structa Cloud</span>
              </div>
            </div>
          </motion.div>

          {/* Back Button */}
          <div className="flex justify-center">
            <BackButton onClick={handleBackNavigation} disabled={isNavigating} text={t('common.backToHome')} />
          </div>
        </motion.div>

      {/* Success Toast */}
      <AnimatePresence>
        {submitStatus === 'success' && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-teal-500 text-white px-6 py-3 
              rounded-xl flex items-center gap-2 shadow-lg z-50"
          >
            <FaCheck className="text-xl" />
            {t('about.successToast')}
          </motion.div>
        )}

        {submitStatus === 'error' && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-red-500 text-white px-6 py-3 
              rounded-xl flex items-center gap-2 max-w-md shadow-lg z-50"
          >
            <FaExclamationTriangle className="text-xl" />
            <span>{errorMessage}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </PageLayout>
  );
}


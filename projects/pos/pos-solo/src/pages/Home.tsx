import { FaClipboardList, FaChartBar, FaHistory, FaCog, FaHeart, FaBoxes, FaUsers, FaMortarPestle, FaFileAlt } from 'react-icons/fa';
import { MdPointOfSale } from 'react-icons/md';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Settings } from '../types';
import PageLayout from '../components/PageLayout';
import { useTranslation } from 'react-i18next';
import defaultLogo from '../assets/pos-crest.svg';

import { isTauri } from '../utils/tauri';

export default function Home() {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, x: -50 },
    show: {
      opacity: 1,
      x: 0,
      transition: {
        type: "spring" as const,
        stiffness: 100,
        damping: 12
      }
    }
  };

  const iconAnimation = {
    initial: { scale: 0 },
    animate: {
      scale: 1,
      transition: {
        type: "spring" as const,
        stiffness: 260,
        damping: 20
      }
    }
  };

  const { t } = useTranslation();
  const navigate = useNavigate();
  const [restaurantName, setRestaurantName] = useState('POS');
  const [logo, setLogo] = useState<string | null>(null);
  const [loadingRoute, setLoadingRoute] = useState<string | null>(null);

  const handleNavigation = (route: string) => {
    setLoadingRoute(route);
    setTimeout(() => {
      navigate(route);
    }, 300);
  };

  useEffect(() => {
    const loadSettings = async () => {
      if (!isTauri) {
        // Browser dev mode — use default branding
        setRestaurantName('Forge');
        return;
      }
      try {
        const response = await invoke<Settings>('get_settings');
        if (response) {
          if (response.restaurant_name) {
            setRestaurantName(response.restaurant_name);
          }
          if (response.logo) {
            setLogo(response.logo);
          }
        }
      } catch (error) {
        console.error('Error loading settings:', error);
        setRestaurantName('Forge');
      }
    };

    loadSettings();
  }, []);

  return (
    <PageLayout
      showNav={false}
      background="bg-linear-to-br from-slate-100 via-purple-100 to-slate-100 dark:from-slate-900 dark:via-purple-900 dark:to-slate-900"
      padding="py-16 md:py-20 lg:py-16"
    >

        {/* Header */}
        <motion.div
          className="text-center mb-12 md:mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            initial={iconAnimation.initial}
            animate={iconAnimation.animate}
            whileHover={{ rotate: 360 }}
            transition={{ duration: 0.6 }}
            className="bg-white/20 dark:bg-white/10 backdrop-blur-sm rounded-full p-6 w-fit mx-auto mb-6 shadow-lg"
          >
            <img
              src={logo || defaultLogo}
              alt="Restaurant Logo"
              className="w-16 h-16 md:w-20 md:h-20 object-contain"
              onError={(e) => {
                // If both custom and bundled logo fail, fall back to an icon
                e.currentTarget.style.display = 'none';
              }}
            />
          </motion.div>
          <motion.h1
            className="text-3xl md:text-4xl lg:text-5xl font-bold text-transparent bg-clip-text 
              bg-linear-to-r from-teal-600 to-purple-600 dark:from-teal-400 dark:to-purple-400 py-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {restaurantName}
          </motion.h1>
        </motion.div>

        {/* Navigation Buttons */}
        <motion.div
          className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4 md:gap-5 max-w-7xl mx-auto px-2"
          variants={container}
          initial="hidden"
          animate="show"
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: "-50px" }}
        >
          <motion.button
            variants={item}
            onClick={() => handleNavigation('/manager')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
            className="flex flex-col items-center p-6 lg:p-5 bg-linear-to-br from-blue-400 to-blue-500 
            dark:from-blue-500 dark:to-blue-600 text-white rounded-2xl transition-all duration-300
            backdrop-blur-sm bg-opacity-90 h-full relative shadow-lg hover:shadow-xl border border-white/10"
            disabled={loadingRoute !== null}
          >
            {loadingRoute === '/manager' ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-10 h-10 mb-2 border-4 border-white border-t-transparent rounded-full"
                />
                <span className="text-lg lg:text-base font-semibold text-center">{t('common.loading')}</span>
              </>
            ) : (
              <>
                <FaClipboardList className="w-10 h-10 mb-2" />
                <span className="text-lg lg:text-base font-semibold text-center leading-tight">{t('nav.productManager')}</span>
                <span className="text-[11px] text-white/70 mt-1 text-center leading-tight max-w-[120px]">{t('nav.productManagerDesc')}</span>
              </>
            )}
          </motion.button>

          <motion.button
            variants={item}
            onClick={() => handleNavigation('/sale')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
            className="flex flex-col items-center p-6 lg:p-5 bg-linear-to-br from-green-400 to-green-500 
            dark:from-green-500 dark:to-green-600 text-white rounded-2xl transition-all duration-300
            backdrop-blur-sm bg-opacity-90 h-full relative shadow-lg hover:shadow-xl border border-white/10"
            disabled={loadingRoute !== null}
          >
            {loadingRoute === '/sale' ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-10 h-10 mb-2 border-4 border-white border-t-transparent rounded-full"
                />
                <span className="text-lg lg:text-base font-semibold text-center">{t('common.loading')}</span>
              </>
            ) : (
              <>
                <MdPointOfSale className="w-10 h-10 mb-2" />
                <span className="text-lg lg:text-base font-semibold text-center leading-tight">{t('nav.newSale')}</span>
                <span className="text-[11px] text-white/70 mt-1 text-center leading-tight max-w-[120px]">{t('nav.newSaleDesc')}</span>
              </>
            )}
          </motion.button>

          <motion.button
            variants={item}
            onClick={() => handleNavigation('/analytics')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
            className="flex flex-col items-center p-6 lg:p-5 bg-linear-to-br from-purple-400 to-purple-500 
            dark:from-purple-500 dark:to-purple-600 text-white rounded-2xl transition-all duration-300
            backdrop-blur-sm bg-opacity-90 h-full relative shadow-lg hover:shadow-xl border border-white/10"
            disabled={loadingRoute !== null}
          >
            {loadingRoute === '/analytics' ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-10 h-10 mb-2 border-4 border-white border-t-transparent rounded-full"
                />
                <span className="text-lg lg:text-base font-semibold text-center">{t('common.loading')}</span>
              </>
            ) : (
              <>
                <FaChartBar className="w-10 h-10 mb-2" />
                <span className="text-lg lg:text-base font-semibold text-center leading-tight">{t('nav.analytics')}</span>
                <span className="text-[11px] text-white/70 mt-1 text-center leading-tight max-w-[120px]">{t('nav.analyticsDesc')}</span>
              </>
            )}
          </motion.button>

          <motion.button
            variants={item}
            onClick={() => handleNavigation('/transactions')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
            className="flex flex-col items-center p-6 lg:p-5 bg-linear-to-br from-orange-400 to-orange-500 
            dark:from-orange-500 dark:to-orange-600 text-white rounded-2xl transition-all duration-300
            backdrop-blur-sm bg-opacity-90 h-full relative shadow-lg hover:shadow-xl border border-white/10"
            disabled={loadingRoute !== null}
          >
            {loadingRoute === '/transactions' ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-10 h-10 mb-2 border-4 border-white border-t-transparent rounded-full"
                />
                <span className="text-lg lg:text-base font-semibold text-center">{t('common.loading')}</span>
              </>
            ) : (
              <>
                <FaHistory className="w-10 h-10 mb-2" />
                <span className="text-lg lg:text-base font-semibold text-center leading-tight">{t('nav.transactions')}</span>
                <span className="text-[11px] text-white/70 mt-1 text-center leading-tight max-w-[120px]">{t('nav.transactionsDesc')}</span>
              </>
            )}
          </motion.button>

          <motion.button
            variants={item}
            onClick={() => handleNavigation('/inventory')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
            className="flex flex-col items-center p-6 lg:p-5 bg-linear-to-br from-emerald-400 to-emerald-500 
            dark:from-emerald-500 dark:to-emerald-600 text-white rounded-2xl transition-all duration-300
            backdrop-blur-sm bg-opacity-90 h-full relative shadow-lg hover:shadow-xl border border-white/10"
            disabled={loadingRoute !== null}
          >
            {loadingRoute === '/inventory' ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-10 h-10 mb-2 border-4 border-white border-t-transparent rounded-full"
                />
                <span className="text-lg lg:text-base font-semibold text-center">{t('common.loading')}</span>
              </>
            ) : (
              <>
                <FaBoxes className="w-10 h-10 mb-2" />
                <span className="text-lg lg:text-base font-semibold text-center leading-tight">{t('nav.inventory')}</span>
                <span className="text-[11px] text-white/70 mt-1 text-center leading-tight max-w-[120px]">{t('nav.inventoryDesc')}</span>
              </>
            )}
          </motion.button>

          <motion.button
            variants={item}
            onClick={() => handleNavigation('/employees')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
            className="flex flex-col items-center p-6 lg:p-5 bg-linear-to-br from-indigo-400 to-indigo-500 
            dark:from-indigo-500 dark:to-indigo-600 text-white rounded-2xl transition-all duration-300
            backdrop-blur-sm bg-opacity-90 h-full relative shadow-lg hover:shadow-xl border border-white/10"
            disabled={loadingRoute !== null}
          >
            {loadingRoute === '/employees' ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-10 h-10 mb-2 border-4 border-white border-t-transparent rounded-full"
                />
                <span className="text-lg lg:text-base font-semibold text-center">{t('common.loading')}</span>
              </>
            ) : (
              <>
                <FaUsers className="w-10 h-10 mb-2" />
                <span className="text-lg lg:text-base font-semibold text-center leading-tight">{t('nav.employees')}</span>
                <span className="text-[11px] text-white/70 mt-1 text-center leading-tight max-w-[120px]">{t('nav.employeesDesc')}</span>
              </>
            )}
          </motion.button>

          <motion.button
            variants={item}
            onClick={() => handleNavigation('/recipes')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
            className="flex flex-col items-center p-6 lg:p-5 bg-linear-to-br from-orange-400 to-orange-500 
            dark:from-orange-500 dark:to-orange-600 text-white rounded-2xl transition-all duration-300
            backdrop-blur-sm bg-opacity-90 h-full relative shadow-lg hover:shadow-xl border border-white/10"
            disabled={loadingRoute !== null}
          >
            {loadingRoute === '/recipes' ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-10 h-10 mb-2 border-4 border-white border-t-transparent rounded-full"
                />
                <span className="text-lg lg:text-base font-semibold text-center">{t('common.loading')}</span>
              </>
            ) : (
              <>
                <FaMortarPestle className="w-10 h-10 mb-2" />
                <span className="text-lg lg:text-base font-semibold text-center leading-tight">{t('nav.recipes')}</span>
                <span className="text-[11px] text-white/70 mt-1 text-center leading-tight max-w-[120px]">{t('nav.recipesDesc')}</span>
              </>
            )}
          </motion.button>

          <motion.button
            variants={item}
            onClick={() => handleNavigation('/reports')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
            className="flex flex-col items-center p-6 lg:p-5 bg-linear-to-br from-rose-400 to-rose-500 
            dark:from-rose-500 dark:to-rose-600 text-white rounded-2xl transition-all duration-300
            backdrop-blur-sm bg-opacity-90 h-full relative shadow-lg hover:shadow-xl border border-white/10"
            disabled={loadingRoute !== null}
          >
            {loadingRoute === '/reports' ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-10 h-10 mb-2 border-4 border-white border-t-transparent rounded-full"
                />
                <span className="text-lg lg:text-base font-semibold text-center">{t('common.loading')}</span>
              </>
            ) : (
              <>
                <FaFileAlt className="w-10 h-10 mb-2" />
                <span className="text-lg lg:text-base font-semibold text-center leading-tight">{t('nav.reports')}</span>
                <span className="text-[11px] text-white/70 mt-1 text-center leading-tight max-w-[120px]">{t('nav.reportsDesc')}</span>
              </>
            )}
          </motion.button>

          <motion.button
            variants={item}
            onClick={() => handleNavigation('/settings')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
            className="flex flex-col items-center p-6 lg:p-5 bg-linear-to-br from-gray-400 to-gray-500 
            dark:from-gray-500 dark:to-gray-600 text-white rounded-2xl transition-all duration-300
            backdrop-blur-sm bg-opacity-90 h-full relative shadow-lg hover:shadow-xl border border-white/10"
            disabled={loadingRoute !== null}
          >
            {loadingRoute === '/settings' ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-10 h-10 mb-2 border-4 border-white border-t-transparent rounded-full"
                />
                <span className="text-lg lg:text-base font-semibold text-center">{t('common.loading')}</span>
              </>
            ) : (
              <>
                <FaCog className="w-10 h-10 mb-2" />
                <span className="text-lg lg:text-base font-semibold text-center leading-tight">{t('nav.settings')}</span>
                <span className="text-[11px] text-white/70 mt-1 text-center leading-tight max-w-[120px]">{t('nav.settingsDesc')}</span>
              </>
            )}
          </motion.button>

          <motion.button
            variants={item}
            onClick={() => handleNavigation('/about')}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.98 }}
            className="flex flex-col items-center p-6 lg:p-5 bg-linear-to-br from-pink-400 to-pink-500 
            dark:from-pink-500 dark:to-pink-600 text-white rounded-2xl transition-all duration-300
            backdrop-blur-sm bg-opacity-90 h-full relative shadow-lg hover:shadow-xl border border-white/10"
            disabled={loadingRoute !== null}
          >
            {loadingRoute === '/about' ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-10 h-10 mb-2 border-4 border-white border-t-transparent rounded-full"
                />
                <span className="text-lg lg:text-base font-semibold text-center">{t('common.loading')}</span>
              </>
            ) : (
              <>
                <FaHeart className="w-10 h-10 mb-2" />
                <span className="text-lg lg:text-base font-semibold text-center leading-tight">{t('nav.about')}</span>
                <span className="text-[11px] text-white/70 mt-1 text-center leading-tight max-w-[120px]">{t('nav.aboutDesc')}</span>
              </>
            )}
          </motion.button>


        </motion.div>
    </PageLayout>
  );
}


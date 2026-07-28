import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// ── Icons use Tabler icon CSS classes via icon-[tabler--*] ──
import { useTranslation } from 'react-i18next';

interface DatePickerProps {
  value: string;
  onChange: (value: string) => void;
  label: string;
}

export default function DatePicker({ value, onChange, label }: DatePickerProps) {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth());
  const [showMonthDropdown, setShowMonthDropdown] = useState(false);
  const [showYearDropdown, setShowYearDropdown] = useState(false);
  const [monthSearch, setMonthSearch] = useState('');
  const [yearSearch, setYearSearch] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);
  const monthDropdownRef = useRef<HTMLDivElement>(null);
  const yearDropdownRef = useRef<HTMLDivElement>(null);
  const monthSearchRef = useRef<HTMLInputElement>(null);
  const yearSearchRef = useRef<HTMLInputElement>(null);

  // Initialize from value if provided
  useEffect(() => {
    if (value) {
      const date = new Date(value);
      setSelectedYear(date.getFullYear());
      setSelectedMonth(date.getMonth());
    }
  }, [value]);

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setShowMonthDropdown(false);
        setShowYearDropdown(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Close dropdowns on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (monthDropdownRef.current && !monthDropdownRef.current.contains(event.target as Node)) {
        setShowMonthDropdown(false);
      }
      if (yearDropdownRef.current && !yearDropdownRef.current.contains(event.target as Node)) {
        setShowYearDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const formatDate = (dateStr: string) => {
    if (!dateStr) return t('datePicker.selectDate');
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  const getDaysInMonth = (year: number, month: number) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (year: number, month: number) => {
    return new Date(year, month, 1).getDay();
  };

  const handleDateSelect = (day: number) => {
    const date = new Date(selectedYear, selectedMonth, day);
    const dateStr = date.toISOString().split('T')[0];
    onChange(dateStr);
    setIsOpen(false);
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange('');
    setIsOpen(false);
  };

  const daysInMonth = getDaysInMonth(selectedYear, selectedMonth);
  const firstDay = getFirstDayOfMonth(selectedYear, selectedMonth);
  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);
  const emptyDays = Array.from({ length: firstDay }, (_, i) => i);

  const months = t('datePicker.months', { returnObjects: true }) as string[];

  const years = Array.from({ length: 20 }, (_, i) => new Date().getFullYear() - 10 + i);

  // Filter months based on search
  const filteredMonths = months.filter(month => 
    month.toLowerCase().includes(monthSearch.toLowerCase())
  );

  // Filter years based on search or generate extended range if typing custom year
  const getFilteredYears = () => {
    if (yearSearch) {
      const searchNum = parseInt(yearSearch);
      if (!isNaN(searchNum)) {
        // If typing a valid year, include it in the list
        const extendedYears = [...years];
        if (!extendedYears.includes(searchNum) && searchNum >= 1900 && searchNum <= 2100) {
          extendedYears.push(searchNum);
          extendedYears.sort((a, b) => b - a);
        }
        return extendedYears.filter(year => year.toString().includes(yearSearch));
      }
    }
    return years;
  };

  const filteredYears = getFilteredYears();

  const selectedDate = value ? new Date(value).getDate() : null;

  // Focus search input when dropdown opens
  useEffect(() => {
    if (showMonthDropdown && monthSearchRef.current) {
      monthSearchRef.current.focus();
    }
  }, [showMonthDropdown]);

  useEffect(() => {
    if (showYearDropdown && yearSearchRef.current) {
      yearSearchRef.current.focus();
    }
  }, [showYearDropdown]);

  return (
    <div ref={containerRef} className="relative">
      <label className="block text-base-content mb-2">{label}</label>
      <div className="relative">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="input input-bordered w-full cursor-pointer flex items-center justify-between"
        >
          <span className={value ? 'text-base-content' : 'text-gray-500 dark:text-gray-400'}>
            {formatDate(value)}
          </span>
          <svg className="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </button>

        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="card bg-base-100 shadow-xl border border-base-300 rounded-xl p-4 absolute z-50 mt-2 w-full min-w-[280px]"
            >
              {/* Month/Year Selectors */}
              <div className="flex gap-2 mb-4">
                {/* Custom Month Dropdown */}
                <div ref={monthDropdownRef} className="flex-1 relative">
                  <button
                    type="button"
                    onClick={() => {
                      setShowMonthDropdown(!showMonthDropdown);
                      setShowYearDropdown(false);
                      setMonthSearch('');
                    }}
                    className="select select-bordered w-full text-sm flex items-center justify-between"
                  >
                    <span>{months[selectedMonth]}</span>
                    <span className={`icon-[tabler--chevron-down] w-5 h-5 transition-transform ${showMonthDropdown ? 'rotate-180' : ''}`} />
                  </button>
                  
                  <AnimatePresence>
                    {showMonthDropdown && (
                      <motion.div
                        initial={{ opacity: 0, y: -5 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -5 }}
                        transition={{ duration: 0.15 }}
                        className="absolute z-60 mt-1 w-full bg-white dark:bg-slate-700 rounded-lg 
                          border border-slate-300 dark:border-slate-600 shadow-xl overflow-hidden"
                      >
                        {/* Search Input */}
                        <div className="p-2 border-b border-slate-300 dark:border-slate-600">
                          <input
                            ref={monthSearchRef}
                            type="text"
                            value={monthSearch}
                            onChange={(e) => setMonthSearch(e.target.value)}
                            placeholder={t('datePicker.searchMonth')}
                            className="input input-bordered input-sm w-full"
                            onClick={(e) => e.stopPropagation()}
                          />
                        </div>
                        
                        {/* Month List */}
                        <div className="max-h-[180px] overflow-y-auto overflow-y-auto">
                          {filteredMonths.length > 0 ? (
                            filteredMonths.map((month, idx) => {
                              const originalIdx = months.indexOf(month);
                              return (
                                <button
                                  key={idx}
                                  type="button"
                                  onClick={() => {
                                    setSelectedMonth(originalIdx);
                                    setShowMonthDropdown(false);
                                    setMonthSearch('');
                                  }}
                                  className={`w-full px-3 py-2 text-left text-sm hover:bg-primary/20 
                                    dark:hover:bg-primary/30 transition-colors
                                    ${selectedMonth === originalIdx 
                                      ? 'bg-primary text-white hover:bg-teal-600' 
                                      : 'text-base-content'
                                    }`}
                                >
                                  {month}
                                </button>
                              );
                            })
                          ) : (
                            <div className="px-3 py-4 text-sm text-center text-base-content/50">
                              {t('datePicker.noMonths')}
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* Custom Year Dropdown */}
                <div ref={yearDropdownRef} className="relative">
                  <button
                    type="button"
                    onClick={() => {
                      setShowYearDropdown(!showYearDropdown);
                      setShowMonthDropdown(false);
                      setYearSearch('');
                    }}
                    className="select select-bordered text-sm flex items-center justify-between gap-2 min-w-[100px]"
                  >
                    <span>{selectedYear}</span>
                    <span className={`icon-[tabler--chevron-down] w-5 h-5 transition-transform ${showYearDropdown ? 'rotate-180' : ''}`} />
                  </button>
                  
                  <AnimatePresence>
                    {showYearDropdown && (
                      <motion.div
                        initial={{ opacity: 0, y: -5 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -5 }}
                        transition={{ duration: 0.15 }}
                        className="absolute z-60 mt-1 w-full bg-white dark:bg-slate-700 rounded-lg 
                          border border-slate-300 dark:border-slate-600 shadow-xl overflow-hidden"
                      >
                        {/* Search/Custom Input */}
                        <div className="p-2 border-b border-slate-300 dark:border-slate-600">
                          <input
                            ref={yearSearchRef}
                            type="text"
                            value={yearSearch}
                            onChange={(e) => {
                              const value = e.target.value;
                              // Only allow numbers
                              if (value === '' || /^\d+$/.test(value)) {
                                setYearSearch(value);
                              }
                            }}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' && yearSearch) {
                                const year = parseInt(yearSearch);
                                if (!isNaN(year) && year >= 1900 && year <= 2100) {
                                  setSelectedYear(year);
                                  setShowYearDropdown(false);
                                  setYearSearch('');
                                }
                              }
                            }}
                            placeholder={t('datePicker.typeYear')}
                            className="input input-bordered input-sm w-full"
                            onClick={(e) => e.stopPropagation()}
                          />
                          {yearSearch && (
                            <div className="mt-1 text-xs text-base-content/50 px-1">
                              {t('datePicker.pressEnter')}
                            </div>
                          )}
                        </div>
                        
                        {/* Year List */}
                        <div className="max-h-[180px] overflow-y-auto overflow-y-auto">
                          {filteredYears.length > 0 ? (
                            filteredYears.map((year) => (
                              <button
                                key={year}
                                type="button"
                                onClick={() => {
                                  setSelectedYear(year);
                                  setShowYearDropdown(false);
                                  setYearSearch('');
                                }}
                                className={`w-full px-3 py-2 text-left text-sm hover:bg-primary/20 
                                  dark:hover:bg-primary/30 transition-colors
                                  ${selectedYear === year 
                                    ? 'bg-primary text-white hover:bg-teal-600' 
                                    : 'text-base-content'
                                  }`}
                              >
                                {year}
                              </button>
                            ))
                          ) : (
                            <div className="px-3 py-4 text-sm text-center text-base-content/50">
                              {yearSearch ? t('datePicker.yearHint') : t('datePicker.noYears')}
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>

              {/* Calendar Grid */}
              <div className="grid grid-cols-7 gap-1 mb-3">
                {(t('datePicker.daysShort', { returnObjects: true }) as string[]).map((day) => (
                  <div key={day} className="text-center text-xs text-base-content/60 font-medium py-1">
                    {day}
                  </div>
                ))}
                {emptyDays.map((_, idx) => (
                  <div key={`empty-${idx}`} />
                ))}
                {days.map((day) => {
                  const isSelected = selectedDate === day && 
                    value && 
                    new Date(value).getMonth() === selectedMonth &&
                    new Date(value).getFullYear() === selectedYear;
                  
                  return (
                    <button
                      key={day}
                      type="button"
                      onClick={() => handleDateSelect(day)}
                      className={`
                        p-2 text-sm rounded hover:bg-primary hover:text-white transition-colors
                        ${isSelected 
                          ? 'bg-primary text-white font-semibold' 
                          : 'text-base-content hover:bg-primary/20'}
                      `}
                    >
                      {day}
                    </button>
                  );
                })}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2 pt-3 border-t border-slate-300 dark:border-slate-600">
                <button
                  type="button"
                  onClick={handleClear}
                  className="                  btn btn-ghost btn-sm flex-1"
                >
                  {t('datePicker.clear')}
                </button>
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="                  btn btn-primary btn-sm flex-1"
                >
                  {t('datePicker.done')}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}


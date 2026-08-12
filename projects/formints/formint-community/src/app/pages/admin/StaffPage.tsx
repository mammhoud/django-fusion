import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { iconClass } from '../../../lib/icons';
import Employees from './Employees';
import EmployeeSchedule from './EmployeeSchedule';

type StaffTab = 'employees' | 'schedule';

const staffTabs: { key: StaffTab; labelKey: string; icon: string }[] = [
  { key: 'employees', labelKey: 'nav.employees', icon: 'users' },
  { key: 'schedule', labelKey: 'nav.schedule', icon: 'calendar-clock' },
];

/**
 * Merged Staff page with tab navigation between Employees and Schedule.
 * Each sub-page manages its own PageLayout, so this wrapper only provides the
 * tab bar — no outer PageLayout to avoid double-nesting.
 */
export default function StaffPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<StaffTab>('employees');

  return (
    <>
      {/* ── Fixed Tab Navigation ── */}
      <div className="sticky top-0 z-20 bg-base-200/80 backdrop-blur-md border-b border-base-300/50">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="tabs tabs-boxed gap-1" role="tablist">
            {staffTabs.map(tab => (
              <button
                key={tab.key}
                type="button"
                role="tab"
                className={`tab gap-2 ${activeTab === tab.key ? 'tab-active' : ''}`}
                onClick={() => setActiveTab(tab.key)}
                aria-selected={activeTab === tab.key}
                aria-controls={`staff-panel-${tab.key}`}
              >
                <span className={iconClass(tab.icon, 'w-4 h-4')} />
                <span className="hidden sm:inline">{t(tab.labelKey)}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Tab Content — each sub-page has its own PageLayout ── */}
      {activeTab === 'employees' && (
        <div id="staff-panel-employees" role="tabpanel" aria-labelledby="staff-tab-employees">
          <Employees />
        </div>
      )}
      {activeTab === 'schedule' && (
        <div id="staff-panel-schedule" role="tabpanel" aria-labelledby="staff-tab-schedule">
          <EmployeeSchedule />
        </div>
      )}
    </>
  );
}

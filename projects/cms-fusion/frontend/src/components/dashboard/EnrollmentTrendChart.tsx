'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';

interface EnrollmentTrendChartProps {
  data: { month: string; count: number }[];
}

const monthLabels: Record<string, string> = {
  '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
  '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
  '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec',
};

function formatMonth(month: string): string {
  const parts = month.split('-');
  const label = monthLabels[parts[1]] || month;
  return `${label} ${parts[0].slice(2)}`;
}

export default function EnrollmentTrendChart({ data }: EnrollmentTrendChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
        No enrollment data yet
      </div>
    );
  }

  const chartData = data.map((d) => ({
    month: formatMonth(d.month),
    enrollments: d.count,
  }));

  // Use a hardcoded hex for SVG gradient (CSS vars don't evaluate inside SVG <defs>)
  const CTC_TEAL = '#00a1b3';

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="enrollmentGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CTC_TEAL} stopOpacity={0.2} />
              <stop offset="95%" stopColor={CTC_TEAL} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
          <XAxis
            dataKey="month"
            tick={{ fontSize: 11, fill: '#6b7280' }}
            axisLine={{ stroke: '#e5e7eb' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#6b7280' }}
            axisLine={false}
            tickLine={false}
            allowDecimals={false}
          />
          <Tooltip
            formatter={(value: number) => [value, 'Enrollments']}
            contentStyle={{
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              fontSize: '13px',
            }}
          />
          <Area
            type="monotone"
            dataKey="enrollments"
            stroke={CTC_TEAL}
            fill="url(#enrollmentGradient)"
            strokeWidth={2}
            dot={{ r: 3, fill: CTC_TEAL, strokeWidth: 0 }}
            activeDot={{ r: 5, fill: CTC_TEAL, strokeWidth: 2, stroke: '#fff' }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

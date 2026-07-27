'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface RevenueChartProps {
  data: { month: string; amount: number }[];
}

const monthLabels: Record<string, string> = {
  '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
  '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
  '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec',
};

function formatMonth(month: string): string {
  // month is "YYYY-MM" format
  const parts = month.split('-');
  const label = monthLabels[parts[1]] || month;
  return `${label} ${parts[0].slice(2)}`;
}

const formatCurrency = (value: number) => `$${value.toLocaleString()}`;

export default function RevenueChart({ data }: RevenueChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
        No revenue data yet
      </div>
    );
  }

  const chartData = data.map((d) => ({
    month: formatMonth(d.month),
    revenue: d.amount,
  }));

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
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
            tickFormatter={(v: number) => `$${v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}`}
          />
          <Tooltip
            formatter={(value: number) => [formatCurrency(value), 'Revenue']}
            contentStyle={{
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              fontSize: '13px',
            }}
          />
          {/* Note: CSS vars don't evaluate inside SVG. Use a hardcoded hex. */}
          <Bar
            dataKey="revenue"
            fill="#00a1b3"
            radius={[4, 4, 0, 0]}
            maxBarSize={48}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

'use client';

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';

interface CompletionRateChartProps {
  completionRate: number;
  completedEnrollments: number;
  activeEnrollments: number;
  totalEnrollments: number;
}

const COLORS = {
  completed: '#22c55e',
  active: '#00a1b3',
  other: '#f59e0b',
};

export default function CompletionRateChart({
  completionRate,
  completedEnrollments,
  activeEnrollments,
  totalEnrollments,
}: CompletionRateChartProps) {
  const otherEnrollments = totalEnrollments - completedEnrollments - activeEnrollments;

  if (totalEnrollments === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
        No enrollment data yet
      </div>
    );
  }

  const pieData = [
    { name: 'Completed', value: completedEnrollments, color: COLORS.completed },
    { name: 'In Progress', value: activeEnrollments, color: COLORS.active },
  ];

  if (otherEnrollments > 0) {
    pieData.push({ name: 'Other', value: otherEnrollments, color: COLORS.other });
  }

  return (
    <div className="w-full">
      <div className="flex items-center justify-center mb-2">
        <div className="text-center">
          <div className="text-3xl font-bold text-gray-900">{completionRate}%</div>
          <div className="text-xs text-gray-500 mt-0.5">Completion Rate</div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={80}
            paddingAngle={2}
            dataKey="value"
          >
            {pieData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number, name: string) => [value, name]}
            contentStyle={{
              borderRadius: '8px',
              border: '1px solid #e5e7eb',
              fontSize: '13px',
            }}
          />
          <Legend
            verticalAlign="bottom"
            height={30}
            iconType="circle"
            iconSize={8}
            formatter={(value: string) => (
              <span className="text-xs text-gray-600">{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="grid grid-cols-3 gap-2 mt-1 text-center text-xs text-gray-500">
        <div>
          <div className="font-semibold text-green-600">{completedEnrollments}</div>
          <div>Completed</div>
        </div>
        <div>
          <div className="font-semibold" style={{ color: 'rgb(var(--fu-primary))' }}>{activeEnrollments}</div>
          <div>In Progress</div>
        </div>
        <div>
          <div className="font-semibold text-amber-500">{otherEnrollments}</div>
          <div>Other</div>
        </div>
      </div>
    </div>
  );
}

import React from 'react';
import {
	BarChart,
	Bar,
	XAxis,
	YAxis,
	CartesianGrid,
	Tooltip,
	Legend,
	ResponsiveContainer,
	Cell,
} from 'recharts';

interface ProbabilityChartProps {
	probabilityUp: number;
	probabilityDown: number;
}

export const ProbabilityChart: React.FC<ProbabilityChartProps> = ({
	probabilityUp,
	probabilityDown,
}) => {
  const data = [
    {
      direction: 'UP',
      probability: probabilityUp * 100,
      fill: '#00D09C', // Groww mint green
    },
    {
      direction: 'DOWN',
      probability: probabilityDown * 100,
      fill: '#F23645', // TradingView sharp red
    },
  ];

  return (
    <div className="glass-panel p-6 flex flex-col h-full">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 tracking-tight">
        AI Prediction Model
      </h3>
      <div className="flex-1 w-full" style={{ minHeight: '350px' }}>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={data} margin={{ top: 20, right: 30, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2D3748" vertical={false} opacity={0.4} />
            <XAxis dataKey="direction" stroke="#718096" tick={{ fill: '#718096', fontSize: 12, fontWeight: 'bold' }} tickLine={false} axisLine={false} dy={10} />
            <YAxis
              stroke="#718096"
              tickFormatter={(value) => `${value}%`}
              domain={[0, 100]}
              tick={{ fill: '#718096', fontSize: 12 }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#121212',
                border: '1px solid #27272A',
                borderRadius: '12px',
                color: '#fff',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}
              formatter={(value: number | string) => [`${Number(value).toFixed(2)}%`, 'Probability']}
              cursor={{ fill: '#27272A', opacity: 0.4 }}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <Bar dataKey="probability" name="Probability" radius={[4, 4, 0, 0]} maxBarSize={60}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

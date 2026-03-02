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
			fill: '#10b981',
		},
		{
			direction: 'DOWN',
			probability: probabilityDown * 100,
			fill: '#ef4444',
		},
	];

	return (
		<div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
			<h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
				Prediction Probability
			</h3>
			<ResponsiveContainer width="100%" height={300}>
				<BarChart data={data}>
					<CartesianGrid strokeDasharray="3 3" stroke="#374151" />
					<XAxis dataKey="direction" stroke="#6b7280" />
					<YAxis
						stroke="#6b7280"
						tickFormatter={(value) => `${value}%`}
						domain={[0, 100]}
					/>
					<Tooltip
						contentStyle={{
							backgroundColor: '#1f2937',
							border: 'none',
							borderRadius: '8px',
							color: '#fff',
						}}
						formatter={(value: any) => [`${Number(value).toFixed(2)}%`, 'Probability']}
					/>
					<Legend />
					<Bar dataKey="probability" name="Probability">
						{data.map((entry, index) => (
							<Cell key={`cell-${index}`} fill={entry.fill} />
						))}
					</Bar>
				</BarChart>
			</ResponsiveContainer>
		</div>
	);
};
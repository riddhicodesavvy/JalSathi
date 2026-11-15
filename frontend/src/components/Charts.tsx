import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Model } from "../types";
const colors = ["#087bd1", "#08bca9", "#6ca4dd", "#49c4d7", "#155688"];
export function PerformanceChart({
  models,
  metric = "accuracy",
}: {
  models: Model[];
  metric?: "accuracy" | "precision" | "recall" | "f1" | "roc_auc";
}) {
  return (
    <div className="chart" role="img" aria-label={`Model ${metric} comparison`}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={models.map((m) => ({
            name: m.name,
            [metric]: m.metrics[metric],
            f1: m.metrics.f1,
          }))}
          margin={{ top: 20, right: 10, bottom: 15, left: 0 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            vertical={false}
            stroke="#dbeaf1"
          />
          <XAxis dataKey="name" fontSize={11} interval={0} />
          <YAxis
            domain={[0, 1]}
            tickFormatter={(v) => `${v * 100}%`}
            width={42}
            fontSize={11}
          />
          <Tooltip formatter={(v) => `${(Number(v) * 100).toFixed(1)}%`} />
          <Legend />
          <Bar dataKey={metric} fill="#078cc1" radius={[5, 5, 0, 0]} />
          {metric !== "f1" && (
            <Bar dataKey="f1" fill="#10bfa8" radius={[5, 5, 0, 0]} />
          )}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
export function DistributionChart({
  classes,
}: {
  classes: Record<string, number>;
}) {
  return (
    <div
      className="chart"
      role="img"
      aria-label={`Dataset distribution: ${classes["0"]} non-potable and ${classes["1"]} potable`}
    >
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={[
              { name: "Non-potable", value: classes["0"] },
              { name: "Potable", value: classes["1"] },
            ]}
            dataKey="value"
            innerRadius={68}
            outerRadius={100}
            paddingAngle={4}
          >
            {[0, 1].map((c, i) => (
              <Cell key={c} fill={colors[i]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

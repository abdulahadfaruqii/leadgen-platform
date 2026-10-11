"use client";

interface ChartBar {
  label: string;
  value: number;
  color?: string;
}

interface ChartBarsProps {
  data: ChartBar[];
  maxHeight?: number;
}

export function ChartBars({ data, maxHeight = 160 }: ChartBarsProps) {
  const max = Math.max(...data.map((d) => d.value));

  return (
    <div className="flex items-end gap-3 h-[180px] pt-5">
      {data.map((bar, i) => {
        const height = max > 0 ? (bar.value / max) * maxHeight : 0;
        return (
          <div key={i} className="flex-1 flex flex-col items-center gap-2 group">
            <span className="text-xs font-bold text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity">
              {bar.value}
            </span>
            <div
              className="w-full rounded-t-md bg-gradient-to-t from-indigo-600 to-purple-500 opacity-80 group-hover:opacity-100 transition-all duration-300"
              style={{ height: `${Math.max(height, 8)}px` }}
            />
            <span className="text-[11px] text-slate-500 font-medium">{bar.label}</span>
          </div>
        );
      })}
    </div>
  );
}

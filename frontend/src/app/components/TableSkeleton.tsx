export default function TableSkeleton({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="kinetic-glass rounded-2xl overflow-hidden p-4">
      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex gap-4 animate-pulse">
            {Array.from({ length: columns }).map((_, j) => (
              <div
                key={j}
                className="h-4 bg-white/10 rounded"
                style={{ width: `${[30, 25, 20, 15, 10][j % 5]}%` }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function LoadingSpinner({ fullScreen = false, message = "Loading..." }) {
  const wrapperClass = fullScreen
    ? "fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90 p-4"
    : "flex items-center justify-center py-8";

  return (
    <div className={wrapperClass}>
      <div className="flex flex-col items-center gap-3 rounded-3xl border border-slate-800 bg-slate-900/95 px-6 py-6 text-center text-white shadow-lg">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-transparent border-t-indigo-400" />
        <p className="text-sm text-slate-300">{message}</p>
      </div>
    </div>
  );
}

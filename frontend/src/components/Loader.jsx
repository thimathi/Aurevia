const Loader = () => (
  <div className="flex items-center gap-3 text-sm text-slate-600">
    <div className="h-4 w-4 animate-spin rounded-full border-2 border-aurora-500 border-t-transparent" aria-hidden="true" />
    <span>Analyzing text and voice signals…</span>
  </div>
);

export default Loader;

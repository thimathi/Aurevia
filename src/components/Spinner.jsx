export default function Spinner() {
  return (
    <div className="flex items-center gap-3 text-slate-200">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-400 border-t-transparent" />
      <span className="text-sm">Running multimodal analysis...</span>
    </div>
  );
}

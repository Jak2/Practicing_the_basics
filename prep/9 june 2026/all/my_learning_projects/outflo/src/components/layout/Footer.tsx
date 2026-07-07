export default function Footer({ className }: { className?: string }) {
  return (
    <footer className={`mt-20 border-t-2 border-neo-black dark:border-white bg-cream dark:bg-neo-black ${className ?? ""}`}>
      <div className="max-w-6xl mx-auto px-4 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-[0.875em] font-black text-neo-black dark:text-white">
          © {new Date().getFullYear()}{" "}
          <span className="bg-neo-yellow px-1 rounded-sm">Outflo</span>
        </p>
        <p className="text-[0.875em] font-medium text-[#777] dark:text-[#777]">
          Outcome-driven AI workflows for real-world problems.
        </p>
      </div>
    </footer>
  );
}

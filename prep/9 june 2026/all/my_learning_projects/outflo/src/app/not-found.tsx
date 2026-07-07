import Link from "next/link";

export default function NotFound() {
  return (
    <div className="max-w-lg mx-auto px-4 py-24 text-center">
      <div className="inline-block border-2 border-neo-black dark:border-white bg-neo-yellow px-6 py-3 rounded-2xl shadow-neo mb-6">
        <span className="text-[3em] font-black text-neo-black">404</span>
      </div>
      <h1 className="text-[2.25em] font-black text-neo-black dark:text-white mb-3">
        Page not found
      </h1>
      <p className="text-[0.875em] text-[#666] dark:text-[#999] mb-8">
        This page does not exist or has been moved.
      </p>
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-[0.875em] font-bold border-2 border-neo-black dark:border-white bg-white dark:bg-[#1A1A1A] px-5 py-2.5 rounded-xl shadow-neo dark:shadow-neo-white hover:bg-neo-yellow hover:text-neo-black hover:shadow-neo-sm hover:translate-x-0.5 hover:translate-y-0.5 transition-all"
      >
        Go Home
      </Link>
    </div>
  );
}

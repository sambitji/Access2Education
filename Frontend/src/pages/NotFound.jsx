import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-16 text-center">
      <div className="max-w-xl rounded-3xl border border-gray-200 bg-white p-10 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-indigo-600">404 error</p>
        <h1 className="mt-6 text-5xl font-bold tracking-tight text-slate-900">Page not found</h1>
        <p className="mt-4 text-base leading-7 text-slate-600">
          Sorry, we couldn’t find the page you’re looking for.
        </p>
        <div className="mt-8">
          <Link
            to="/"
            className="inline-flex items-center rounded-full bg-indigo-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700"
          >
            Go back home
          </Link>
        </div>
      </div>
    </div>
  );
}

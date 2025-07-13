'use client';

import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="w-full bg-[#181A1B] px-8 py-3 flex items-center justify-between shadow-md">
      <div className="flex items-center space-x-2">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-green-400 font-bold text-2xl">●●</span>
          <span className="text-white font-bold text-xl tracking-wide">Movie Recommendation Engine</span>
          <span className="text-green-400 font-bold text-2xl">●●</span>
        </Link>
      </div>
      <div className="flex items-center space-x-6 text-gray-300">
        <Link href="/films" className="hover:text-white transition-colors">FILMS</Link>
        <Link href="/account" className="hover:text-white transition-colors">MY ACCOUNT</Link>
        <Link href="/upload" className="ml-6 bg-green-500 hover:bg-green-600 text-white font-bold px-4 py-1 rounded transition-colors">UPLOAD</Link>

      </div>
    </nav>
  );
}
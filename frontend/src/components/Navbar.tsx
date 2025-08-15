'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';

interface User {
  id: number;
  username: string;
  email: string;
}

export default function Navbar() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  useEffect(() => {
    const fetchCurrentUser = async () => {
      const savedToken = localStorage.getItem('authToken');
      if (savedToken) {
        try {
          const response = await fetch('http://localhost:8000/api/auth/me', {
            headers: {
              'Authorization': `Bearer ${savedToken}`,
            },
          });

          if (response.ok) {
            const user = await response.json();
            setCurrentUser(user);
          }
        } catch (error) {
          console.error('Error fetching user:', error);
        }
      }
    };

    fetchCurrentUser();
  }, []);

  return (
    <nav className="w-full bg-transparent px-8 py-3 flex items-center justify-between relative z-30 m-0">
      <div className="font-montserrat flex items-center space-x-2">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-green-400 font-bold text-2xl">●●</span>
          <span className="text-white font-bold text-xl tracking-wide" style={{ fontFamily: 'var(--font-dm-serif-display)' }}>Movie Recommendation Engine</span>
          <span className="text-green-400 font-bold text-2xl">●●</span>
        </Link>
      </div>
      <div className="flex items-center space-x-6 text-gray-500">
        <Link href="/weekly" className="hover:text-white transition-colors font-inter font-semibold">WEEKLY</Link>
        <Link href="/account" className="hover:text-white transition-colors font-inter font-semibold">
          {currentUser ? currentUser.username.toUpperCase() : 'MY ACCOUNT'}
        </Link>
        <Link href="/upload" className="ml-6 bg-green-500 hover:bg-green-600 text-white font-bold px-4 py-1 rounded transition-colors font-inter">UPLOAD</Link>
      </div>
    </nav>
  );
}
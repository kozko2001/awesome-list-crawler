'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Search, Shuffle, List } from 'lucide-react';

export function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: 'Timeline', icon: Home },
    { href: '/search', label: 'Search', icon: Search },
    { href: '/sources', label: 'Sources', icon: List },
    { href: '/lucky', label: 'Lucky', icon: Shuffle },
  ];

  return (
    <nav className="border-b border-terminal-border bg-terminal-bg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="hover:text-terminal-green transition-colors duration-200">
              <h1 className="text-xl font-bold glow-text">
                $ awesome-crawler<span className="cursor"></span>
              </h1>
            </Link>
          </div>

          {/* Navigation Links */}
          <div className="flex space-x-8">
            {navItems.map(({ href, label, icon: Icon }) => {
              const isActive = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center space-x-2 px-3 py-2 text-sm font-mono transition-colors duration-200 ${
                    isActive
                      ? 'text-terminal-green border-b border-terminal-green'
                      : 'text-terminal-text hover:text-terminal-green'
                  }`}
                >
                  <Icon size={16} />
                  <span>{label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
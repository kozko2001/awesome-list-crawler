'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { Home, Search, Shuffle, List, Menu, X } from 'lucide-react';

export function Navigation() {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navItems = [
    { href: '/', label: 'Timeline', icon: Home },
    { href: '/search', label: 'Search', icon: Search },
    { href: '/sources', label: 'Sources', icon: List },
    { href: '/lucky', label: 'Lucky', icon: Shuffle },
  ];

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <nav className="border-b border-terminal-border bg-terminal-bg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="hover:text-terminal-green transition-colors duration-200" onClick={closeMobileMenu}>
              <h1 className="text-lg sm:text-xl font-bold glow-text">
                <span className="hidden sm:inline">$ awesome-crawler</span>
                <span className="sm:hidden">$ awesome</span>
                <span className="cursor"></span>
              </h1>
            </Link>
          </div>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex space-x-6 lg:space-x-8">
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

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={toggleMobileMenu}
              className="text-terminal-text hover:text-terminal-green transition-colors duration-200 p-2"
              aria-label="Toggle mobile menu"
            >
              {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-terminal-border bg-terminal-bg">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navItems.map(({ href, label, icon: Icon }) => {
                const isActive = pathname === href;
                return (
                  <Link
                    key={href}
                    href={href}
                    onClick={closeMobileMenu}
                    className={`flex items-center space-x-3 px-3 py-3 text-base font-mono transition-colors duration-200 rounded-none border-l-2 ${
                      isActive
                        ? 'text-terminal-green border-l-terminal-green bg-terminal-green/10'
                        : 'text-terminal-text hover:text-terminal-green border-l-transparent hover:border-l-terminal-green hover:bg-terminal-green/5'
                    }`}
                  >
                    <Icon size={18} />
                    <span>{label}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
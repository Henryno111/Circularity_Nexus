'use client';

import React, { useState, useEffect } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { Moon, Sun, Leaf, Menu, X, ChevronDown } from 'lucide-react';

export default function Navbar() {
  const { theme, toggleTheme, mounted } = useTheme();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { href: '#home', label: 'Home' },
    { href: '#features', label: 'Features' },
    { href: '#how-it-works', label: 'How It Works' },
    { href: '#impact', label: 'Impact' },
  ];

  const handleLinkClick = (href: string) => {
    setIsMobileMenuOpen(false);
    // Smooth scroll to section
    const element = document.querySelector(href);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <>
      <nav 
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled 
            ? 'bg-white/95 dark:bg-emerald-950/95 backdrop-blur-lg shadow-lg shadow-emerald-500/5' 
            : 'bg-white/80 dark:bg-emerald-950/80 backdrop-blur-md'
        }`}
      >
        <div className="w-full">
          <div className="w-full flex items-center justify-between h-16 lg:h-20 px-8 sm:px-12 lg:px-16 xl:px-20 2xl:px-24">
            {/* Logo */}
            <div className="flex items-center space-x-3 cursor-pointer" onClick={() => handleLinkClick('#home')}>
              <div className="relative">
                <div className="flex items-center justify-center w-10 h-10 lg:w-12 lg:h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl shadow-lg shadow-emerald-500/25">
                  <Leaf className="w-5 h-5 lg:w-6 lg:h-6 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              </div>
              <div className="flex flex-col">
                <span className="text-xl lg:text-2xl font-bold text-gray-900 dark:text-white font-display">
                  Circularity
                </span>
                <span className="text-xs lg:text-sm text-emerald-600 dark:text-emerald-400 font-semibold -mt-1 tracking-wider">
                  NEXUS
                </span>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center gap-8 lg:gap-12 xl:gap-16 2xl:gap-20">
              {navLinks.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={(e) => {
                    e.preventDefault();
                    handleLinkClick(link.href);
                  }}
                  className="relative px-6 py-3 text-gray-700 dark:text-gray-200 hover:text-emerald-600 dark:hover:text-emerald-400 font-medium text-base lg:text-lg xl:text-xl transition-all duration-200 group whitespace-nowrap"
                >
                  {link.label}
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-emerald-500 to-emerald-600 group-hover:w-full transition-all duration-300"></span>
                </a>
              ))}
            </div>

            {/* Right Side - Theme Toggle & CTA */}
            <div className="flex items-center gap-6 lg:gap-8 xl:gap-10">
              {/* Theme Toggle */}
              {mounted && (
                <button
                  onClick={toggleTheme}
                  className="relative p-3 lg:p-4 rounded-xl bg-gray-100 dark:bg-emerald-800/50 text-gray-600 dark:text-emerald-300 hover:bg-gray-200 dark:hover:bg-emerald-700 transition-all duration-200 group"
                  aria-label="Toggle theme"
                >
                  <div className="relative w-5 h-5 lg:w-6 lg:h-6">
                    <Sun className={`absolute inset-0 transform transition-all duration-300 ${theme === 'light' ? 'rotate-0 opacity-100' : 'rotate-90 opacity-0'}`} />
                    <Moon className={`absolute inset-0 transform transition-all duration-300 ${theme === 'dark' ? 'rotate-0 opacity-100' : '-rotate-90 opacity-0'}`} />
                  </div>
                </button>
              )}

              {/* CTA Button - Desktop */}
              <button className="hidden sm:flex items-center px-16 lg:px-12
               py-4 lg:py-5 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white text-sm lg:text-base font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 hover:scale-105">
                Get Started
              </button>

              {/* Mobile menu button */}
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="lg:hidden p-3 rounded-xl bg-gray-100 dark:bg-emerald-800/50 text-gray-600 dark:text-emerald-300 hover:bg-gray-200 dark:hover:bg-emerald-700 transition-all duration-200"
                aria-label="Toggle mobile menu"
              >
                <div className="relative w-6 h-6">
                  <Menu className={`absolute inset-0 transform transition-all duration-300 ${isMobileMenuOpen ? 'rotate-90 opacity-0' : 'rotate-0 opacity-100'}`} />
                  <X className={`absolute inset-0 transform transition-all duration-300 ${isMobileMenuOpen ? 'rotate-0 opacity-100' : '-rotate-90 opacity-0'}`} />
                </div>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Menu */}
      <div
        className={`fixed inset-0 z-40 transform transition-all duration-300 lg:hidden ${
          isMobileMenuOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Backdrop */}
        <div 
          className="absolute inset-0 bg-black/20 backdrop-blur-sm"
          onClick={() => setIsMobileMenuOpen(false)}
        />
        
        {/* Menu Panel */}
        <div className="absolute right-0 top-0 h-full w-80 max-w-[85vw] bg-white dark:bg-emerald-950 shadow-2xl">
          <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-emerald-800">
              <div className="flex items-center space-x-3">
                <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl">
                  <Leaf className="w-5 h-5 text-white" />
                </div>
                <div>
                  <span className="text-lg font-bold text-gray-900 dark:text-white font-display">Circularity</span>
                  <span className="block text-xs text-emerald-600 dark:text-emerald-400 font-semibold">NEXUS</span>
                </div>
              </div>
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-emerald-800"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Navigation Links */}
            <div className="flex-1 py-6">
              <div className="space-y-3 px-6">
                {navLinks.map((link) => (
                  <a
                    key={link.href}
                    href={link.href}
                    onClick={(e) => {
                      e.preventDefault();
                      handleLinkClick(link.href);
                    }}
                    className="flex items-center justify-between px-6 py-4 text-gray-700 dark:text-gray-200 hover:text-emerald-600 dark:hover:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-800/50 rounded-xl font-medium transition-all duration-200 group"
                  >
                    {link.label}
                    <ChevronDown className="w-4 h-4 rotate-[-90deg] opacity-0 group-hover:opacity-100 transition-all duration-200" />
                  </a>
                ))}
              </div>
            </div>

            {/* Bottom CTA */}
            <div className="p-6 border-t border-gray-200 dark:border-emerald-800">
              <button className="w-full px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-emerald-500/25">
                Get Started
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
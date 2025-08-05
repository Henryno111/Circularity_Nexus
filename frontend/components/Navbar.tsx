'use client';

import React from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { Moon, Sun, Leaf } from 'lucide-react';

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 dark:bg-emerald-900/90 backdrop-blur-md border-b border-emerald-100 dark:border-emerald-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center justify-center w-10 h-10 bg-emerald-500 rounded-xl">
              <Leaf className="w-6 h-6 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-emerald-900 dark:text-white">
                Circularity
              </span>
              <span className="text-xs text-emerald-600 dark:text-emerald-300 -mt-1">
                NEXUS
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            <a 
              href="#home" 
              className="text-emerald-800 dark:text-emerald-100 hover:text-emerald-600 dark:hover:text-white transition-colors duration-200 font-medium"
            >
              Home
            </a>
            <a 
              href="#features" 
              className="text-emerald-800 dark:text-emerald-100 hover:text-emerald-600 dark:hover:text-white transition-colors duration-200 font-medium"
            >
              Features
            </a>
            <a 
              href="#how-it-works" 
              className="text-emerald-800 dark:text-emerald-100 hover:text-emerald-600 dark:hover:text-white transition-colors duration-200 font-medium"
            >
              How It Works
            </a>
            <a 
              href="#impact" 
              className="text-emerald-800 dark:text-emerald-100 hover:text-emerald-600 dark:hover:text-white transition-colors duration-200 font-medium"
            >
              Impact
            </a>
            <a 
              href="#contact" 
              className="text-emerald-800 dark:text-emerald-100 hover:text-emerald-600 dark:hover:text-white transition-colors duration-200 font-medium"
            >
              Contact
            </a>
          </div>

          {/* Theme Toggle & CTA */}
          <div className="flex items-center space-x-4">
            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl bg-emerald-100 dark:bg-emerald-800 text-emerald-600 dark:text-emerald-300 hover:bg-emerald-200 dark:hover:bg-emerald-700 transition-all duration-200"
              aria-label="Toggle theme"
            >
              {theme === 'light' ? (
                <Moon className="w-5 h-5" />
              ) : (
                <Sun className="w-5 h-5" />
              )}
            </button>

            {/* CTA Button */}
            <button className="hidden sm:flex items-center px-6 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl font-semibold transition-all duration-200 shadow-lg shadow-emerald-500/25">
              Get Started
            </button>

            {/* Mobile Menu Button */}
            <button className="md:hidden p-2 rounded-xl bg-emerald-100 dark:bg-emerald-800 text-emerald-600 dark:text-emerald-300">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
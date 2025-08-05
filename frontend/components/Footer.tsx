'use client';

import React from 'react';
import { 
  Leaf, 
  Twitter, 
  Github, 
  Linkedin, 
  Mail,
  ArrowRight,
  Heart
} from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-emerald-900 dark:bg-emerald-950 text-white">
      <div className="max-w-7xl mx-auto w-full px-6 sm:px-8 lg:px-12 xl:px-16 2xl:px-24">
        {/* Main Footer Content */}
        <div className="py-16">
          <div className="grid lg:grid-cols-4 gap-8 lg:gap-12 xl:gap-16 2xl:gap-20">
            {/* Company Info */}
            <div className="lg:col-span-2 space-y-6">
              {/* Logo */}
              <div className="flex items-center space-x-3">
                <div className="flex items-center justify-center w-12 h-12 bg-emerald-500 rounded-2xl">
                  <Leaf className="w-7 h-7 text-white" />
                </div>
                <div className="flex flex-col">
                  <span className="text-2xl font-bold text-white">
                    Circularity
                  </span>
                  <span className="text-sm text-emerald-300 -mt-1">
                    NEXUS
                  </span>
                </div>
              </div>

              {/* Description */}
              <p className="text-lg text-emerald-100 leading-relaxed max-w-md">
                Revolutionary waste-to-wealth tokenization platform. Transform your trash into tradeable tokens, 
                carbon credits, and real rewards while healing our planet.
              </p>

              {/* Tagline */}
              <div className="inline-flex items-center px-4 py-2 bg-emerald-800 rounded-full text-emerald-200 text-sm font-semibold">
                <Heart className="w-4 h-4 mr-2 text-red-400" />
                Tokenize Trash. Earn Wealth. Heal the Planet.
              </div>

              {/* Social Links */}
              <div className="flex space-x-4">
                <a 
                  href="#" 
                  className="p-3 bg-emerald-800 hover:bg-emerald-700 rounded-xl transition-colors duration-200"
                  aria-label="Twitter"
                >
                  <Twitter className="w-5 h-5" />
                </a>
                <a 
                  href="#" 
                  className="p-3 bg-emerald-800 hover:bg-emerald-700 rounded-xl transition-colors duration-200"
                  aria-label="GitHub"
                >
                  <Github className="w-5 h-5" />
                </a>
                <a 
                  href="#" 
                  className="p-3 bg-emerald-800 hover:bg-emerald-700 rounded-xl transition-colors duration-200"
                  aria-label="LinkedIn"
                >
                  <Linkedin className="w-5 h-5" />
                </a>
                <a 
                  href="#" 
                  className="p-3 bg-emerald-800 hover:bg-emerald-700 rounded-xl transition-colors duration-200"
                  aria-label="Email"
                >
                  <Mail className="w-5 h-5" />
                </a>
              </div>
            </div>

            {/* Quick Links */}
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-white">Platform</h3>
              <div className="space-y-3">
                <a href="#features" className="block text-emerald-200 hover:text-white transition-colors duration-200">
                  Features
                </a>
                <a href="#how-it-works" className="block text-emerald-200 hover:text-white transition-colors duration-200">
                  How It Works
                </a>
                <a href="#" className="block text-emerald-200 hover:text-white transition-colors duration-200">
                  Mobile App
                </a>
                <a href="#" className="block text-emerald-200 hover:text-white transition-colors duration-200">
                  API Documentation
                </a>
                <a href="#" className="block text-emerald-200 hover:text-white transition-colors duration-200">
                  Smart Contracts
                </a>
              </div>
            </div>

            {/* Resources */}
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-white">Resources</h3>
              <div className="space-y-3">
                <a href="#" className="block text-emerald-200 hover:text-white transition-colors duration-200">
                  Whitepaper
                </a>
                <a href="#" className="block text-emerald-200 hover:text-white transition-colors duration-200">
                  Blog
                </a>
                <a href="#" className="block text-emerald-200 hover:text-white transition-colors duration-200">
                  Help Center
                </a>
                <a href="#" className="block text-emerald-200 hover:text-white transition-colors duration-200">
                  Community
                </a>
                <a href="#" className="block text-emerald-200 hover:text-white transition-colors duration-200">
                  Carbon Impact Report
                </a>
              </div>
            </div>
          </div>

          {/* Newsletter Signup */}
          <div className="mt-16 pt-12 border-t border-emerald-800">
            <div className="lg:flex lg:items-center lg:justify-between">
              <div className="lg:w-0 lg:flex-1">
                <h3 className="text-2xl font-bold text-white mb-2">
                  Stay Updated
                </h3>
                <p className="text-emerald-200">
                  Get the latest updates on our platform, new features, and environmental impact.
                </p>
              </div>
              <div className="mt-6 lg:mt-0 lg:ml-8">
                <div className="flex flex-col sm:flex-row gap-3">
                  <input
                    type="email"
                    placeholder="Enter your email"
                    className="px-4 py-3 bg-emerald-800 text-white placeholder-emerald-300 rounded-xl border border-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent min-w-[300px]"
                  />
                  <button className="inline-flex items-center px-6 py-3 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl font-semibold transition-all duration-200 shadow-lg shadow-emerald-500/25">
                    Subscribe
                    <ArrowRight className="ml-2 w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="py-8 border-t border-emerald-800">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            {/* Copyright */}
            <div className="text-emerald-200 text-sm">
              © 2024 Circularity Nexus. All rights reserved. Built with 💚 for a sustainable future.
            </div>

            {/* Legal Links */}
            <div className="flex space-x-6">
              <a href="#" className="text-emerald-200 hover:text-white text-sm transition-colors duration-200">
                Privacy Policy
              </a>
              <a href="#" className="text-emerald-200 hover:text-white text-sm transition-colors duration-200">
                Terms of Service
              </a>
              <a href="#" className="text-emerald-200 hover:text-white text-sm transition-colors duration-200">
                Cookie Policy
              </a>
            </div>
          </div>

          {/* Environmental Impact */}
          <div className="mt-6 pt-6 border-t border-emerald-800/50">
            <div className="text-center">
              <p className="text-emerald-300 text-sm mb-3">
                🌍 Environmental Impact to Date
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                <div>
                  <div className="text-2xl font-bold text-emerald-400">2.5M</div>
                  <div className="text-xs text-emerald-200">Tons Recycled</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-emerald-400">1.8M</div>
                  <div className="text-xs text-emerald-200">CO₂ Reduced</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-emerald-400">50K</div>
                  <div className="text-xs text-emerald-200">Active Users</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-emerald-400">$12M</div>
                  <div className="text-xs text-emerald-200">Rewards Paid</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
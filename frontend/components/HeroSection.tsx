'use client';

import React from 'react';
import { ArrowRight, Recycle, Coins, Leaf } from 'lucide-react';

export default function HeroSection() {
  return (
    <section id="home" className="relative min-h-screen flex items-center overflow-hidden">
      {/* Background with Image Placeholder */}
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-50 via-white to-emerald-100 dark:from-emerald-900 dark:via-emerald-800 dark:to-emerald-900">
        {/* Image Placeholder - Replace with your hero image */}
        <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 to-green-400/10 dark:from-emerald-600/20 dark:to-green-500/20">
          <div className="absolute inset-0 flex items-center justify-center text-emerald-300/30 dark:text-emerald-700/30">
            <div className="text-center">
              <div className="text-6xl font-bold mb-4">📸</div>
              <div className="text-xl font-medium">Hero Image Placeholder</div>
              <div className="text-sm mt-2">Replace with your choice of background image</div>
            </div>
          </div>
        </div>
        
        {/* Overlay for better text readability */}
        <div className="absolute inset-0 bg-white/40 dark:bg-emerald-900/60"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Text Content */}
          <div className="space-y-8">
            {/* Badge */}
            <div className="inline-flex items-center px-4 py-2 bg-emerald-100 dark:bg-emerald-800/50 rounded-full text-emerald-800 dark:text-emerald-200 text-sm font-semibold">
              <Leaf className="w-4 h-4 mr-2" />
              Tokenize Trash. Earn Wealth. Heal the Planet.
            </div>

            {/* Main Heading */}
            <div className="space-y-4">
              <h1 className="text-5xl lg:text-6xl xl:text-7xl font-bold text-emerald-900 dark:text-white leading-tight">
                Turn Your
                <span className="text-emerald-500 block">Waste Into</span>
                <span className="bg-gradient-to-r from-emerald-600 to-green-500 bg-clip-text text-transparent block">
                  Wealth
                </span>
              </h1>
              
              <p className="text-xl lg:text-2xl text-emerald-700 dark:text-emerald-200 leading-relaxed max-w-2xl">
                Revolutionary blockchain platform that transforms waste into tradeable tokens, 
                carbon credits, and real rewards. Join the circular economy revolution.
              </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">50+</div>
                <div className="text-sm text-emerald-700 dark:text-emerald-300">Waste Types</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">25%</div>
                <div className="text-sm text-emerald-700 dark:text-emerald-300">Max APY</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">95%</div>
                <div className="text-sm text-emerald-700 dark:text-emerald-300">AI Accuracy</div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="group inline-flex items-center px-8 py-4 bg-emerald-500 hover:bg-emerald-600 text-white rounded-2xl font-semibold text-lg transition-all duration-200 shadow-xl shadow-emerald-500/25">
                Start Tokenizing
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform duration-200" />
              </button>
              
              <button className="inline-flex items-center px-8 py-4 bg-white/80 dark:bg-emerald-800/80 text-emerald-700 dark:text-emerald-200 rounded-2xl font-semibold text-lg border border-emerald-200 dark:border-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-700 transition-all duration-200">
                Watch Demo
              </button>
            </div>
          </div>

          {/* Right Column - Feature Cards */}
          <div className="space-y-6">
            {/* Feature Card 1 */}
            <div className="bg-white/70 dark:bg-emerald-800/40 backdrop-blur-sm rounded-3xl p-6 border border-emerald-100 dark:border-emerald-700 shadow-lg">
              <div className="flex items-start space-x-4">
                <div className="flex items-center justify-center w-12 h-12 bg-emerald-500 rounded-2xl">
                  <Recycle className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-emerald-900 dark:text-white mb-2">
                    AI-Powered Verification
                  </h3>
                  <p className="text-emerald-700 dark:text-emerald-200">
                    Groq Llama3 validates waste quality and quantity via mobile scanning with 95%+ accuracy.
                  </p>
                </div>
              </div>
            </div>

            {/* Feature Card 2 */}
            <div className="bg-white/70 dark:bg-emerald-800/40 backdrop-blur-sm rounded-3xl p-6 border border-emerald-100 dark:border-emerald-700 shadow-lg">
              <div className="flex items-start space-x-4">
                <div className="flex items-center justify-center w-12 h-12 bg-emerald-500 rounded-2xl">
                  <Coins className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-emerald-900 dark:text-white mb-2">
                    DeFi Recycling Vaults
                  </h3>
                  <p className="text-emerald-700 dark:text-emerald-200">
                    Stake waste tokens and earn up to 25% APY from corporate ESG partners and carbon markets.
                  </p>
                </div>
              </div>
            </div>

            {/* Feature Card 3 */}
            <div className="bg-white/70 dark:bg-emerald-800/40 backdrop-blur-sm rounded-3xl p-6 border border-emerald-100 dark:border-emerald-700 shadow-lg">
              <div className="flex items-start space-x-4">
                <div className="flex items-center justify-center w-12 h-12 bg-emerald-500 rounded-2xl">
                  <Leaf className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-emerald-900 dark:text-white mb-2">
                    Carbon Credit Fusion
                  </h3>
                  <p className="text-emerald-700 dark:text-emerald-200">
                    Automatically convert recycled waste into tradable carbon tokens with real environmental impact.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Elements */}
      <div className="absolute top-20 right-10 w-20 h-20 bg-emerald-200/30 dark:bg-emerald-600/20 rounded-full blur-xl"></div>
      <div className="absolute bottom-20 left-10 w-32 h-32 bg-green-200/30 dark:bg-green-600/20 rounded-full blur-xl"></div>
      <div className="absolute top-1/2 right-1/4 w-16 h-16 bg-emerald-300/30 dark:bg-emerald-500/20 rounded-full blur-xl"></div>
    </section>
  );
}
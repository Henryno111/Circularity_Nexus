'use client';

import React from 'react';
import Image from 'next/image';
import { ArrowRight, Play, Sparkles, TrendingUp, Shield, Zap } from 'lucide-react';

export default function HeroSection() {
  return (
    <section id="home" className="relative min-h-screen flex items-center">
      {/* Background Image */}
      <div className="absolute inset-0 z-0">
        <Image
          src="/hero_image.png"
          alt="Circularity Nexus - Transforming waste into wealth"
          fill
          className="object-cover object-center"
          priority
          quality={95}
        />
        {/* Subtle overlay to maintain image clarity while ensuring text readability */}
        <div className="absolute inset-0 bg-gradient-to-r from-black/20 via-black/10 to-black/20 dark:from-black/40 dark:via-black/20 dark:to-black/40"></div>
      </div>

      {/* Content Container */}
      <div className="relative z-10 w-full">
        <div className="w-full px-6 sm:px-8 lg:px-12 xl:px-16 2xl:px-24 pt-20 lg:pt-24">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 xl:gap-20 2xl:gap-32 items-center min-h-[calc(100vh-8rem)]">
            
            {/* Left Content - Text & CTA */}
            <div className="space-y-8 lg:space-y-10 xl:space-y-12">
              {/* Badge */}
              <div className="inline-flex items-center px-4 py-2 bg-white/90 dark:bg-emerald-900/90 backdrop-blur-sm rounded-full border border-emerald-200/50 dark:border-emerald-700/50 shadow-lg">
                <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400 mr-2" />
                <span className="text-sm font-semibold text-emerald-800 dark:text-emerald-200">
                  Tokenize Trash. Earn Wealth. Heal the Planet.
                </span>
              </div>

              {/* Main Heading */}
              <div className="space-y-4">
                <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold leading-[1.1] text-white drop-shadow-2xl">
                  <span className="block">Transform Your</span>
                  <span className="block bg-gradient-to-r from-emerald-400 via-green-300 to-emerald-500 bg-clip-text text-transparent">
                    Waste Into
                  </span>
                  <span className="block">Digital Wealth</span>
                </h1>
                
                <p className="text-lg sm:text-xl lg:text-2xl text-white/90 leading-relaxed max-w-3xl drop-shadow-lg">
                  Revolutionary blockchain platform powered by AI that transforms everyday waste into tradeable tokens, 
                  carbon credits, and real financial rewards.
                </p>
              </div>

              {/* Stats Row */}
              <div className="grid grid-cols-3 gap-6 lg:gap-8 xl:gap-12 py-8 lg:py-10">
                {[
                  { number: '50+', label: 'Waste Types' },
                  { number: '25%', label: 'Max APY' },
                  { number: '95%', label: 'AI Accuracy' }
                ].map((stat, index) => (
                  <div key={index} className="text-center">
                    <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white drop-shadow-lg">
                      {stat.number}
                    </div>
                    <div className="text-sm sm:text-base text-white/80 font-medium">
                      {stat.label}
                    </div>
                  </div>
                ))}
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-6 lg:gap-8 pt-6">
                <button className="group inline-flex items-center justify-center px-10 py-5 lg:px-12 lg:py-6 xl:px-14 xl:py-7 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white text-lg lg:text-xl xl:text-2xl font-semibold rounded-2xl transition-all duration-300 shadow-2xl shadow-emerald-500/25 hover:shadow-emerald-500/40 hover:scale-105 transform min-w-[200px] lg:min-w-[240px]">
                  <span>Start Tokenizing</span>
                  <ArrowRight className="ml-3 lg:ml-4 w-6 h-6 lg:w-7 lg:h-7 group-hover:translate-x-1 transition-transform duration-200" />
                </button>
                
                <button className="group inline-flex items-center justify-center px-10 py-5 lg:px-12 lg:py-6 xl:px-14 xl:py-7 bg-white/20 hover:bg-white/30 backdrop-blur-sm text-white text-lg lg:text-xl xl:text-2xl font-semibold rounded-2xl border border-white/30 hover:border-white/50 transition-all duration-300 min-w-[180px] lg:min-w-[220px]">
                  <Play className="mr-3 lg:mr-4 w-6 h-6 lg:w-7 lg:h-7" />
                  <span>Watch Demo</span>
                </button>
              </div>
            </div>

            {/* Right Content - Feature Cards */}
            <div className="space-y-6 lg:space-y-8 xl:space-y-10">
              {[
                {
                  icon: Shield,
                  title: 'AI-Powered Verification',
                  description: 'Advanced AI validates waste quality with 95%+ accuracy using computer vision.',
                  gradient: 'from-blue-500 to-cyan-500'
                },
                {
                  icon: TrendingUp,
                  title: 'DeFi Yield Farming',
                  description: 'Stake tokens in ESG vaults and earn up to 25% APY from corporate partners.',
                  gradient: 'from-emerald-500 to-green-500'
                },
                {
                  icon: Zap,
                  title: 'Instant Tokenization',
                  description: 'Convert waste to tokens in seconds on Hedera\'s high-speed blockchain.',
                  gradient: 'from-yellow-500 to-orange-500'
                }
              ].map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <div
                    key={index}
                    className="group bg-white/10 dark:bg-white/5 backdrop-blur-lg rounded-2xl lg:rounded-3xl p-4 lg:p-6 border border-white/20 hover:border-white/30 shadow-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105"
                  >
                    <div className="flex items-start space-x-4">
                      <div className={`flex-shrink-0 w-12 h-12 lg:w-14 lg:h-14 bg-gradient-to-r ${feature.gradient} rounded-xl lg:rounded-2xl flex items-center justify-center shadow-lg`}>
                        <Icon className="w-6 h-6 lg:w-7 lg:h-7 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg lg:text-xl font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors duration-200">
                          {feature.title}
                        </h3>
                        <p className="text-sm lg:text-base text-white/80 leading-relaxed">
                          {feature.description}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-emerald-400 rounded-full animate-pulse opacity-60"></div>
        <div className="absolute top-3/4 right-1/3 w-1 h-1 bg-green-300 rounded-full animate-ping opacity-40"></div>
        <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-emerald-300 rounded-full animate-pulse opacity-50"></div>
        <div className="absolute top-1/2 right-1/4 w-1.5 h-1.5 bg-green-400 rounded-full animate-ping opacity-30"></div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center">
          <div className="w-1 h-3 bg-white/60 rounded-full mt-2 animate-pulse"></div>
        </div>
      </div>
    </section>
  );
}
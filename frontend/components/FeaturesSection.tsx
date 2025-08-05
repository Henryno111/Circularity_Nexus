'use client';

import React from 'react';
import { 
  Smartphone, 
  Brain, 
  Coins, 
  TreePine, 
  Shield, 
  TrendingUp,
  Zap,
  Globe,
  Recycle
} from 'lucide-react';

const features = [
  {
    icon: Smartphone,
    title: "Mobile-First Scanning",
    description: "Snap photos of waste with your phone. Our AI instantly classifies materials and estimates token value.",
    color: "from-emerald-500 to-green-500"
  },
  {
    icon: Brain,
    title: "95% AI Accuracy",
    description: "Groq Llama3-8B powered classification with quality grading from EXCELLENT to UNUSABLE.",
    color: "from-blue-500 to-cyan-500"
  },
  {
    icon: Coins,
    title: "Material-Specific Tokens",
    description: "Different multipliers for 50+ waste types. E-waste gets 2.0x, aluminum 1.5x, organic 0.3x.",
    color: "from-yellow-500 to-orange-500"
  },
  {
    icon: TreePine,
    title: "Carbon Credit Conversion",
    description: "Automatically convert waste tokens to carbon credits. 1kg PET = 1.5kg CO₂ impact reduction.",
    color: "from-green-500 to-emerald-500"
  },
  {
    icon: Shield,
    title: "Blockchain Security",
    description: "Built on Hedera Hashgraph with 10,000 TPS, instant finality, and carbon-negative consensus.",
    color: "from-purple-500 to-violet-500"
  },
  {
    icon: TrendingUp,
    title: "DeFi Yield Farming",
    description: "Stake tokens in corporate ESG vaults. Earn 5-25% APY from companies like Unilever and P&G.",
    color: "from-pink-500 to-rose-500"
  }
];

export default function FeaturesSection() {
  return (
    <section id="features" className="py-20 lg:py-28 xl:py-32 bg-white dark:bg-emerald-900">
      <div className="w-full px-6 sm:px-8 lg:px-12 xl:px-16 2xl:px-24">
        {/* Section Header */}
        <div className="text-center mb-20 lg:mb-24 xl:mb-28">
          <div className="inline-flex items-center px-4 py-2 bg-emerald-100 dark:bg-emerald-800/50 rounded-full text-emerald-800 dark:text-emerald-200 text-sm font-semibold mb-4">
            <Zap className="w-4 h-4 mr-2" />
            Groundbreaking Features
          </div>
          
          <h2 className="text-4xl lg:text-5xl font-bold text-emerald-900 dark:text-white mb-6">
            Why Circularity Nexus is
            <span className="text-emerald-500 block">Revolutionary</span>
          </h2>
          
          <p className="text-xl text-emerald-700 dark:text-emerald-200 max-w-3xl mx-auto">
            The world's first comprehensive waste-to-wealth tokenization platform combining 
            AI verification, DeFi rewards, and real environmental impact.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 lg:gap-10 xl:gap-12 2xl:gap-16">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="group bg-gradient-to-br from-white to-emerald-50 dark:from-emerald-800 dark:to-emerald-900 rounded-3xl p-8 lg:p-10 xl:p-12 border border-emerald-100 dark:border-emerald-700 hover:shadow-2xl hover:shadow-emerald-500/10 transition-all duration-300 hover:-translate-y-2"
              >
                {/* Icon */}
                <div className={`inline-flex items-center justify-center w-16 h-16 lg:w-18 lg:h-18 xl:w-20 xl:h-20 bg-gradient-to-r ${feature.color} rounded-2xl mb-8 lg:mb-10 group-hover:scale-110 transition-transform duration-300`}>
                  <Icon className="w-8 h-8 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-2xl lg:text-3xl xl:text-4xl font-bold text-emerald-900 dark:text-white mb-6 lg:mb-8">
                  {feature.title}
                </h3>
                
                <p className="text-lg lg:text-xl text-emerald-700 dark:text-emerald-200 leading-relaxed">
                  {feature.description}
                </p>

                {/* Hover Arrow */}
                <div className="flex items-center mt-8 lg:mt-10 text-emerald-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <span className="text-base lg:text-lg font-semibold mr-3">Learn more</span>
                  <div className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-20 lg:mt-24 xl:mt-28">
          <div className="bg-gradient-to-r from-emerald-500 to-green-500 rounded-3xl p-12 lg:p-16 xl:p-20 text-white relative overflow-hidden">
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-0 left-0 w-32 h-32 bg-white rounded-full -translate-x-16 -translate-y-16"></div>
              <div className="absolute bottom-0 right-0 w-40 h-40 bg-white rounded-full translate-x-20 translate-y-20"></div>
              <div className="absolute top-1/2 left-1/2 w-24 h-24 bg-white rounded-full -translate-x-12 -translate-y-12"></div>
            </div>
            
            <div className="relative z-10">
              <Globe className="w-16 h-16 mx-auto mb-6" />
              <h3 className="text-3xl font-bold mb-4">
                Ready to Transform Waste into Wealth?
              </h3>
              <p className="text-xl mb-8 max-w-2xl mx-auto opacity-90">
                Join thousands of users already earning rewards while healing the planet. 
                Start your circular economy journey today.
              </p>
              <button className="inline-flex items-center px-8 py-4 bg-white text-emerald-600 rounded-2xl font-semibold text-lg hover:bg-emerald-50 transition-all duration-200 shadow-lg">
                <Recycle className="w-5 h-5 mr-2" />
                Start Tokenizing Now
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
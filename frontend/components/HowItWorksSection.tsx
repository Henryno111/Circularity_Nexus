'use client';

import React from 'react';
import { 
  Camera, 
  Cpu, 
  Coins, 
  TrendingUp,
  ArrowRight,
  CheckCircle
} from 'lucide-react';

const steps = [
  {
    icon: Camera,
    title: "Scan Your Waste",
    description: "Take a photo of your recyclable materials using our mobile app. Our AI instantly identifies the waste type and quality.",
    details: ["50+ waste types supported", "Quality grading system", "GPS location tracking", "Anti-fraud verification"],
    color: "from-blue-500 to-cyan-500"
  },
  {
    icon: Cpu,
    title: "AI Verification",
    description: "Groq Llama3-8B processes your submission with 95%+ accuracy, cross-verifying with smart bin sensor data.",
    details: ["Sub-2 second processing", "95%+ accuracy rate", "Quality assessment", "Market price calculation"],
    color: "from-purple-500 to-violet-500"
  },
  {
    icon: Coins,
    title: "Earn Tokens",
    description: "Receive waste tokens instantly on Hedera blockchain. Different materials have different multipliers based on recycling value.",
    details: ["Instant token minting", "Material-specific rates", "Quality-based rewards", "Blockchain security"],
    color: "from-emerald-500 to-green-500"
  },
  {
    icon: TrendingUp,
    title: "Stake & Earn",
    description: "Stake your tokens in DeFi vaults or convert to carbon credits. Earn up to 25% APY from corporate ESG partners.",
    details: ["5-25% APY rewards", "Carbon credit conversion", "Corporate partnerships", "Flexible staking periods"],
    color: "from-yellow-500 to-orange-500"
  }
];

export default function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-24 bg-white dark:from-emerald-900 dark:via-emerald-800 dark:to-emerald-900">
      <div className="max-w-7xl mx-auto w-full px-6 sm:px-8 lg:px-12 xl:px-16 2xl:px-24">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center px-4 py-2 bg-emerald-100 dark:bg-emerald-800/50 rounded-full text-emerald-800 dark:text-emerald-200 text-sm font-semibold mb-4">
            <CheckCircle className="w-4 h-4 mr-2" />
            Simple Process
          </div>
          
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 dark:text-white mb-6">
            How It Works
            <span className="text-emerald-500 block">In 4 Simple Steps</span>
          </h2>
          
          <p className="text-xl text-gray-500 dark:text-emerald-200 max-w-3xl mx-auto">
            Transform your daily waste into valuable digital assets in minutes. 
            Our streamlined process makes earning from recycling effortless.
          </p>
        </div>

        {/* Steps */}
        <div className="space-y-12">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isEven = index % 2 === 0;
            
            return (
              <div key={index} className="relative">
                {/* Connection Line */}
                {index < steps.length - 1 && (
                  <div className="absolute left-1/2 top-32 w-px h-24 bg-gradient-to-b from-emerald-300 to-emerald-500 dark:from-emerald-600 dark:to-emerald-400 transform -translate-x-px z-0"></div>
                )}
                
                <div className={`grid lg:grid-cols-2 gap-8 lg:gap-12 xl:gap-16 2xl:gap-20 items-center ${isEven ? '' : 'lg:flex-row-reverse'}`}>
                  {/* Content */}
                  <div className={`space-y-6 ${isEven ? 'lg:pr-12' : 'lg:pl-12 lg:order-2'}`}>
                    {/* Step Number */}
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center justify-center w-12 h-12 bg-emerald-500 text-white rounded-2xl font-bold text-xl">
                        {index + 1}
                      </div>
                      <div className="text-sm text-emerald-600 dark:text-emerald-400 font-semibold">
                        STEP {index + 1}
                      </div>
                    </div>

                    {/* Title & Description */}
                    <div>
                      <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                        {step.title}
                      </h3>
                      <p className="text-xl text-gray-500 dark:text-emerald-200 leading-relaxed">
                        {step.description}
                      </p>
                    </div>

                    {/* Details List */}
                    <div className="grid grid-cols-2 gap-3">
                      {step.details.map((detail, detailIndex) => (
                        <div key={detailIndex} className="flex items-center space-x-2">
                          <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                          <span className="text-sm text-gray-600 dark:text-emerald-300">
                            {detail}
                          </span>
                        </div>
                      ))}
                    </div>

                    {/* Arrow for larger screens */}
                    {index < steps.length - 1 && (
                      <div className="hidden lg:flex items-center justify-center pt-8">
                        <ArrowRight className="w-6 h-6 text-emerald-400" />
                      </div>
                    )}
                  </div>

                  {/* Visual Card */}
                  <div className={`${isEven ? '' : 'lg:order-1'}`}>
                    <div className="bg-white dark:bg-emerald-800/50 rounded-3xl p-8 shadow-2xl border border-gray-200 dark:border-emerald-700 relative overflow-hidden">
                      {/* Background Pattern */}
                      <div className="absolute inset-0 opacity-5">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500 rounded-full translate-x-16 -translate-y-16"></div>
                        <div className="absolute bottom-0 left-0 w-24 h-24 bg-green-500 rounded-full -translate-x-12 translate-y-12"></div>
                      </div>

                      <div className="relative z-10 text-center">
                        {/* Icon */}
                        <div className={`inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r ${step.color} rounded-3xl mb-6 shadow-lg`}>
                          <Icon className="w-10 h-10 text-white" />
                        </div>

                        {/* Image Placeholder */}
                        <div className="bg-gradient-to-br from-gray-100 to-gray-200 dark:from-emerald-700 dark:to-green-700 rounded-2xl h-48 flex items-center justify-center mb-6">
                          <div className="text-center text-gray-400 dark:text-emerald-500">
                            <div className="text-4xl mb-2">🖼️</div>
                            <div className="text-sm font-medium">Step {index + 1} Visual</div>
                            <div className="text-xs mt-1">Image Placeholder</div>
                          </div>
                        </div>

                        {/* Stats */}
                        <div className="grid grid-cols-2 gap-4 text-center">
                          <div>
                            <div className="text-2xl font-bold text-gray-900 dark:text-emerald-400">
                              {index === 0 ? '< 3s' : index === 1 ? '95%' : index === 2 ? '10k' : '25%'}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-emerald-300">
                              {index === 0 ? 'Processing' : index === 1 ? 'Accuracy' : index === 2 ? 'TPS' : 'Max APY'}
                            </div>
                          </div>
                          <div>
                            <div className="text-2xl font-bold text-gray-900 dark:text-emerald-400">
                              {index === 0 ? '50+' : index === 1 ? '24/7' : index === 2 ? '$0.0001' : '1M+'}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-emerald-300">
                              {index === 0 ? 'Materials' : index === 1 ? 'Available' : index === 2 ? 'Cost' : 'Tokens'}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Call to Action */}
        <div className="text-center mt-20">
          <div className="bg-white dark:bg-emerald-800 rounded-3xl p-12 shadow-2xl border border-gray-200 dark:border-emerald-700">
            <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
              Ready to Start Your Journey?
            </h3>
            <p className="text-xl text-gray-500 dark:text-emerald-200 mb-8 max-w-2xl mx-auto">
              Join the circular economy revolution. Start earning rewards from your waste today.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="inline-flex items-center px-8 py-4 bg-emerald-500 hover:bg-emerald-600 text-white rounded-2xl font-semibold text-lg transition-all duration-200 shadow-lg shadow-emerald-500/25">
                <Camera className="w-5 h-5 mr-2" />
                Download App
              </button>
              <button className="inline-flex items-center px-8 py-4 bg-gray-100 dark:bg-emerald-700 text-gray-700 dark:text-emerald-200 rounded-2xl font-semibold text-lg hover:bg-gray-200 dark:hover:bg-emerald-600 transition-all duration-200">
                Watch Demo
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
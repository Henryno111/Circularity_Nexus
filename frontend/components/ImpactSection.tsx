'use client';

import React from 'react';
import { 
  TreePine, 
  Droplets, 
  Zap, 
  Recycle,
  TrendingUp,
  Users,
  Globe,
  Award
} from 'lucide-react';

const impactStats = [
  {
    icon: TreePine,
    value: "2.5M",
    unit: "Tons",
    label: "Waste Recycled",
    description: "Diverted from landfills and transformed into valuable resources",
    color: "from-green-500 to-emerald-600"
  },
  {
    icon: Droplets,
    value: "1.8M",
    unit: "Tons CO₂",
    label: "Emissions Reduced",
    description: "Carbon footprint prevented through our recycling network",
    color: "from-blue-500 to-cyan-600"
  },
  {
    icon: Zap,
    value: "45M",
    unit: "kWh",
    label: "Energy Saved",
    description: "Power consumption reduced through efficient recycling processes",
    color: "from-yellow-500 to-orange-600"
  },
  {
    icon: Users,
    value: "150K",
    unit: "Users",
    label: "Active Recyclers",
    description: "Community members actively participating in circular economy",
    color: "from-purple-500 to-violet-600"
  }
];

const features = [
  {
    icon: Award,
    title: "Verified Impact",
    description: "All environmental benefits are verified by third-party auditors and blockchain technology for complete transparency."
  },
  {
    icon: Globe,
    title: "Global Reach",
    description: "Operating in 25+ countries with localized waste management solutions adapted to regional needs."
  },
  {
    icon: TrendingUp,
    title: "Growing Network",
    description: "Our ecosystem grows daily with new corporate partners, recyclers, and environmental initiatives."
  }
];

export default function ImpactSection() {
  return (
    <section id="impact" className="py-24 bg-gradient-to-br from-white via-emerald-50 to-green-50 dark:from-emerald-900 dark:via-emerald-800 dark:to-emerald-900">
      <div className="max-w-7xl mx-auto w-full px-6 sm:px-8 lg:px-12 xl:px-16 2xl:px-24">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center px-4 py-2 bg-emerald-100 dark:bg-emerald-800/50 rounded-full text-emerald-800 dark:text-emerald-200 text-sm font-semibold mb-4">
            <Globe className="w-4 h-4 mr-2" />
            Real Environmental Impact
          </div>
          
          <h2 className="text-4xl lg:text-5xl font-bold text-emerald-900 dark:text-white mb-6">
            Healing Our Planet
            <span className="text-emerald-500 block">One Token at a Time</span>
          </h2>
          
          <p className="text-xl text-emerald-700 dark:text-emerald-200 max-w-3xl mx-auto">
            Every piece of waste tokenized creates measurable environmental impact. 
            Join our growing community in building a sustainable future through blockchain technology.
          </p>
        </div>

        {/* Impact Stats */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 xl:gap-10 2xl:gap-12 mb-20">
          {impactStats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={index}
                className="bg-white dark:bg-emerald-800/50 rounded-3xl p-8 text-center shadow-xl border border-emerald-100 dark:border-emerald-700 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300"
              >
                {/* Icon */}
                <div className={`inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r ${stat.color} rounded-2xl mb-6 shadow-lg`}>
                  <Icon className="w-8 h-8 text-white" />
                </div>

                {/* Stats */}
                <div className="mb-4">
                  <div className="text-4xl font-bold text-emerald-900 dark:text-white mb-1">
                    {stat.value}
                  </div>
                  <div className="text-lg font-semibold text-emerald-600 dark:text-emerald-400">
                    {stat.unit}
                  </div>
                </div>

                {/* Label & Description */}
                <h3 className="text-xl font-bold text-emerald-800 dark:text-emerald-200 mb-3">
                  {stat.label}
                </h3>
                <p className="text-emerald-600 dark:text-emerald-300 text-sm leading-relaxed">
                  {stat.description}
                </p>
              </div>
            );
          })}
        </div>

        {/* Features Grid */}
        <div className="grid lg:grid-cols-3 gap-6 lg:gap-8 xl:gap-10 2xl:gap-12 mb-16">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="bg-white/80 dark:bg-emerald-800/40 backdrop-blur-sm rounded-3xl p-8 border border-emerald-100 dark:border-emerald-700 hover:shadow-lg transition-all duration-300"
              >
                <div className="flex items-center space-x-4 mb-6">
                  <div className="flex items-center justify-center w-12 h-12 bg-emerald-500 rounded-2xl">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-emerald-900 dark:text-white">
                    {feature.title}
                  </h3>
                </div>
                <p className="text-emerald-700 dark:text-emerald-200 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>

        {/* Call to Action */}
        <div className="text-center">
          <div className="bg-gradient-to-r from-emerald-600 to-green-600 rounded-3xl p-12 text-white relative overflow-hidden">
            {/* Background Elements */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-0 left-0 w-40 h-40 bg-white rounded-full -translate-x-20 -translate-y-20"></div>
              <div className="absolute bottom-0 right-0 w-32 h-32 bg-white rounded-full translate-x-16 translate-y-16"></div>
              <div className="absolute top-1/2 left-1/3 w-24 h-24 bg-white rounded-full"></div>
              <div className="absolute bottom-1/4 left-1/4 w-16 h-16 bg-white rounded-full"></div>
            </div>

            <div className="relative z-10 max-w-4xl mx-auto">
              <Recycle className="w-16 h-16 mx-auto mb-6" />
              <h3 className="text-3xl lg:text-4xl font-bold mb-6">
                Ready to Make a Real Difference?
              </h3>
              <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
                Join thousands of users who are already earning rewards while creating positive environmental impact. 
                Every action counts in building a circular economy.
              </p>
              
              {/* Stats Row */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                <div>
                  <div className="text-2xl font-bold">50+</div>
                  <div className="text-sm opacity-80">Waste Types</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">25%</div>
                  <div className="text-sm opacity-80">Max APY</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">95%</div>
                  <div className="text-sm opacity-80">AI Accuracy</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">24/7</div>
                  <div className="text-sm opacity-80">Available</div>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button className="inline-flex items-center px-8 py-4 bg-white text-emerald-600 rounded-2xl font-semibold text-lg hover:bg-emerald-50 transition-all duration-200 shadow-lg">
                  <TreePine className="w-5 h-5 mr-2" />
                  Start Making Impact
                </button>
                <button className="inline-flex items-center px-8 py-4 bg-emerald-700 text-white rounded-2xl font-semibold text-lg hover:bg-emerald-800 transition-all duration-200 border border-emerald-500">
                  Learn More
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Partnership Logos Placeholder */}
        <div className="mt-20 text-center">
          <p className="text-emerald-600 dark:text-emerald-400 text-sm font-semibold mb-8">
            Trusted by leading organizations worldwide
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            {/* Logo Placeholders */}
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="w-32 h-16 bg-emerald-200 dark:bg-emerald-700 rounded-xl flex items-center justify-center"
              >
                <span className="text-emerald-600 dark:text-emerald-300 text-xs font-medium">
                  Partner Logo {i}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
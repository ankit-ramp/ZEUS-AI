'use client';

import { FaRobot, FaChartLine, FaUsers, FaShieldAlt, FaBrain, FaLightbulb } from 'react-icons/fa';
import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center py-12 sm:px-6 lg:px-8">
      <div className="text-center">
        <FaBrain className="mx-auto h-16 w-16 text-blue-600" />
        <h1 className="mt-6 text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
          Welcome to Zeus AI
        </h1>
        <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
          Discover amazing features and services. Join our community and start exploring today!
        </p>
        <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
          <div className="rounded-md shadow">
            <Link href="/login"
              className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10">
              Get started
            </Link>
          </div>
          <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
            <Link href="/features"
              className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10">
              Learn more
            </Link>
          </div>
        </div>
      </div>

      <div className="mt-20 w-full max-w-7xl mx-auto">
        <h2 className="text-center text-3xl font-extrabold text-gray-900 mb-12">Key Features</h2>
        <div className="grid grid-cols-1 gap-y-10 gap-x-6 sm:grid-cols-2 lg:grid-cols-3 lg:gap-x-8">
          {[
            { name: 'AI Powered Insights', icon: FaBrain, description: 'Leverage cutting-edge AI to gain valuable insights from your data.' },
            { name: 'Real-time Analytics', icon: FaChartLine, description: 'Track your performance with up-to-the-minute analytics and reports.' },
            { name: 'Collaborative Tools', icon: FaUsers, description: 'Work together seamlessly with our suite of collaborative features.' },
            { name: 'Top-notch Security', icon: FaShieldAlt, description: 'Your data is protected with industry-leading security measures.' }, 
            { name: 'Intelligent Automation', icon: FaRobot, description: 'Automate repetitive tasks and streamline your workflows.' },
            { name: 'Innovative Solutions', icon: FaLightbulb, description: 'Discover new possibilities with our innovative tools and services.' },
          ].map((feature) => (
            <div key={feature.name} className="bg-white shadow-lg rounded-lg p-6 flex flex-col items-center text-center">
              <feature.icon className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">{feature.name}</h3>
              <p className="text-sm text-gray-500">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 
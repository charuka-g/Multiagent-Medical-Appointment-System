'use client'

import { useState } from 'react'
import ChatWidget from '@/components/ChatWidget'

export default function Home() {
  const [idNumber, setIdNumber] = useState<string>('')

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-slate-50">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-900 rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900">City General Hospital</h1>
                <p className="text-xs text-slate-600">Compassionate Care, Advanced Medicine</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <a href="#" className="text-slate-700 hover:text-blue-900 text-sm font-medium">Services</a>
              <a href="#" className="text-slate-700 hover:text-blue-900 text-sm font-medium">Doctors</a>
              <a href="#" className="text-slate-700 hover:text-blue-900 text-sm font-medium">Contact</a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section with Doctor Image */}
      <section className="relative bg-gradient-to-r from-blue-900 to-blue-950 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            {/* Left Side - Text Content */}
            <div>
              <p className="text-lg text-blue-50 mb-8">
                Schedule appointments, consult with specialists, and manage your healthcare needs with our AI-powered assistant available 24/7.
              </p>
              
              {/* Patient ID Input Section - Prominent */}
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <h3 className="text-lg font-semibold mb-3">Patient Portal Access</h3>
                <p className="text-sm text-blue-100 mb-4">
                  Enter your patient ID to access your account
                </p>
                <div>
                  <label htmlFor="id-number" className="block text-sm font-medium text-white mb-2">
                    Patient ID Number
                  </label>
                  <input
                    id="id-number"
                    type="text"
                    value={idNumber}
                    onChange={(e) => {
                      // Only allow numbers
                      const value = e.target.value.replace(/\D/g, '')
                      setIdNumber(value)
                    }}
                    className="w-full px-4 py-3 bg-white text-slate-900 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none transition-all placeholder:text-slate-400"
                    placeholder="Enter your 8-digit patient ID"
                    maxLength={8}
                  />
                  <p className="text-xs text-blue-100 mt-2">
                    💬 Once entered, click the chat button to start a conversation with our AI assistant
                  </p>
                </div>
              </div>
            </div>

            {/* Right Side - Doctor Image */}
            <div className="relative">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                <img
                  src="/images/doctorimage.jpg"
                  alt="Professional doctor"
                  className="w-full h-auto object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-blue-900/20 to-transparent"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">Our Services</h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Comprehensive healthcare services delivered with care and expertise
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow border border-slate-100">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-blue-900"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3 className="font-semibold text-slate-900 mb-2 text-lg">Smart Appointment Booking</h3>
            <p className="text-sm text-slate-600">
              AI-powered scheduling system that finds the best available time slots for your appointments
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow border border-slate-100">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-blue-900"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="font-semibold text-slate-900 mb-2 text-lg">24/7 AI Assistant</h3>
            <p className="text-sm text-slate-600">
              Get instant help with booking, rescheduling, and managing your medical appointments anytime
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow border border-slate-100">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-blue-900"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="font-semibold text-slate-900 mb-2 text-lg">Easy Management</h3>
            <p className="text-sm text-slate-600">
              Simple and intuitive interface for booking doctor appointments and lab tests
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-slate-400 text-sm">
              © 2024 City General Hospital. All rights reserved.
            </p>
            <p className="text-slate-500 text-xs mt-2">
              For emergencies, please call 911 or visit our emergency department
            </p>
          </div>
        </div>
      </footer>

      {/* Floating Chat Widget */}
      <ChatWidget idNumber={idNumber ? parseInt(idNumber) : 1} />
    </main>
  )
}

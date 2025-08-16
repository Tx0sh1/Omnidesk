import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Ticket, 
  Users, 
  Clock, 
  Shield, 
  Zap, 
  CheckCircle, 
  ArrowRight, 
  Star,
  MessageSquare,
  BarChart3,
  Globe,
  Smartphone
} from 'lucide-react';

const Home: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            <div className="flex justify-center mb-8">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-2xl shadow-lg">
                <Ticket className="h-12 w-12" />
              </div>
            </div>
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">OmniDesk</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              The ultimate help desk solution that streamlines your support process, 
              enhances customer satisfaction, and empowers your team to deliver exceptional service.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/client/submit" 
                className="btn btn-primary text-lg px-8 py-4 shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
              >
                Submit a Ticket
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link 
                to="/client/status" 
                className="btn btn-secondary text-lg px-8 py-4 shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
              >
                Check Status
                <Clock className="ml-2 h-5 w-5" />
              </Link>
            </div>
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full opacity-20 animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-200 rounded-full opacity-20 animate-pulse"></div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Choose OmniDesk?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Powerful features designed to revolutionize your customer support experience
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Zap,
                title: "Lightning Fast",
                description: "Quick ticket resolution with automated workflows and intelligent routing"
              },
              {
                icon: Users,
                title: "Team Collaboration",
                description: "Seamless collaboration tools to keep your team synchronized and productive"
              },
              {
                icon: Shield,
                title: "Enterprise Security",
                description: "Bank-level security with encryption and compliance standards"
              },
              {
                icon: MessageSquare,
                title: "Multi-Channel Support",
                description: "Handle tickets from email, web forms, and multiple communication channels"
              },
              {
                icon: BarChart3,
                title: "Advanced Analytics",
                description: "Comprehensive reporting and insights to optimize your support operations"
              },
              {
                icon: Smartphone,
                title: "Mobile Ready",
                description: "Fully responsive design that works perfectly on all devices"
              }
            ].map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div 
                  key={index}
                  className="card hover:shadow-lg transition-all duration-300 transform hover:-translate-y-2 group"
                >
                  <div className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white p-3 rounded-lg w-fit mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Statistics Section */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Trusted by Businesses Worldwide
            </h2>
            <p className="text-xl opacity-90">
              Join thousands of companies already using OmniDesk
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { number: "10K+", label: "Active Users" },
              { number: "99.9%", label: "Uptime" },
              { number: "24/7", label: "Support" },
              { number: "500+", label: "Companies" }
            ].map((stat, index) => (
              <div key={index} className="transform hover:scale-105 transition-transform duration-300">
                <div className="text-4xl md:text-5xl font-bold mb-2">{stat.number}</div>
                <div className="text-lg opacity-90">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Transform Your Support Experience
              </h2>
              <div className="space-y-4">
                {[
                  "Reduce response time by up to 70%",
                  "Increase customer satisfaction scores",
                  "Streamline team productivity",
                  "Gain valuable insights with analytics",
                  "Scale support operations efficiently"
                ].map((benefit, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <CheckCircle className="h-6 w-6 text-green-500 flex-shrink-0" />
                    <span className="text-lg text-gray-700">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="bg-white rounded-2xl shadow-2xl p-8 transform rotate-3 hover:rotate-0 transition-transform duration-500">
                <div className="flex items-center space-x-4 mb-6">
                  <div className="bg-green-100 p-3 rounded-full">
                    <Star className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Customer Feedback</h4>
                    <p className="text-sm text-gray-600">Real testimonials</p>
                  </div>
                </div>
                <p className="text-gray-700 italic mb-4">
                  "OmniDesk has revolutionized our customer support. Response times are faster, 
                  our team is more organized, and customer satisfaction has never been higher!"
                </p>
                <div className="flex items-center space-x-1">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Experience the power of OmniDesk today. Submit your first ticket or check existing status.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              to="/client/submit" 
              className="btn btn-primary text-lg px-8 py-4 shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
            >
              <Ticket className="mr-2 h-5 w-5" />
              Submit Ticket
            </Link>
            <Link 
              to="/about" 
              className="btn btn-secondary text-lg px-8 py-4 shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
            >
              <Globe className="mr-2 h-5 w-5" />
              Learn More
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;

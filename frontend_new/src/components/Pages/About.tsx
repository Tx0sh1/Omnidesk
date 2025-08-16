import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Ticket, 
  Users, 
  Target, 
  Heart, 
  Shield, 
  Zap, 
  Globe, 
  Mail,
  Phone,
  MapPin,
  Award,
  TrendingUp,
  Clock,
  CheckCircle
} from 'lucide-react';

const About: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 to-indigo-700 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex justify-center mb-8">
            <div className="bg-white/20 backdrop-blur-sm p-4 rounded-2xl">
              <Ticket className="h-12 w-12" />
            </div>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            About OmniDesk
          </h1>
          <p className="text-xl md:text-2xl opacity-90 max-w-3xl mx-auto">
            Empowering businesses with intelligent customer support solutions since day one
          </p>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Our Mission
              </h2>
              <p className="text-lg text-gray-700 mb-6">
                At OmniDesk, we believe that exceptional customer support is the cornerstone of business success. 
                Our mission is to provide businesses of all sizes with powerful, intuitive tools that transform 
                the way they interact with their customers.
              </p>
              <p className="text-lg text-gray-700 mb-8">
                We're committed to making customer support more efficient, more personal, and more impactful 
                through innovative technology and user-centered design.
              </p>
              <div className="flex flex-wrap gap-4">
                {[
                  { icon: Target, text: "Customer-Focused" },
                  { icon: Heart, text: "Passionate Team" },
                  { icon: Shield, text: "Reliable & Secure" }
                ].map((item, index) => {
                  const Icon = item.icon;
                  return (
                    <div key={index} className="flex items-center space-x-2 bg-blue-50 px-4 py-2 rounded-full">
                      <Icon className="h-5 w-5 text-blue-600" />
                      <span className="text-blue-800 font-medium">{item.text}</span>
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="relative">
              <div className="bg-gradient-to-br from-blue-100 to-indigo-100 rounded-2xl p-8">
                <div className="grid grid-cols-2 gap-6">
                  {[
                    { icon: Users, number: "50K+", label: "Happy Customers" },
                    { icon: Globe, number: "40+", label: "Countries" },
                    { icon: Award, number: "99.9%", label: "Uptime" },
                    { icon: TrendingUp, number: "500%", label: "Growth Rate" }
                  ].map((stat, index) => {
                    const Icon = stat.icon;
                    return (
                      <div key={index} className="text-center">
                        <div className="bg-white p-3 rounded-lg shadow-sm w-fit mx-auto mb-3">
                          <Icon className="h-8 w-8 text-blue-600" />
                        </div>
                        <div className="text-2xl font-bold text-gray-900">{stat.number}</div>
                        <div className="text-sm text-gray-600">{stat.label}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              What Makes Us Different
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Our comprehensive platform offers everything you need to deliver exceptional customer support
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Zap,
                title: "Lightning-Fast Performance",
                description: "Built with modern technology stack for optimal speed and reliability. Handle thousands of tickets without breaking a sweat."
              },
              {
                icon: Shield,
                title: "Enterprise-Grade Security",
                description: "Your data is protected with industry-leading security measures, encryption, and compliance standards."
              },
              {
                icon: Users,
                title: "Collaborative Workflows",
                description: "Seamless team collaboration with role-based access, automated assignments, and real-time updates."
              },
              {
                icon: Globe,
                title: "Multi-Channel Support",
                description: "Centralize support from email, web forms, chat, and social media in one unified platform."
              },
              {
                icon: Clock,
                title: "24/7 Availability",
                description: "Round-the-clock system availability with 99.9% uptime guarantee and dedicated support team."
              },
              {
                icon: TrendingUp,
                title: "Advanced Analytics",
                description: "Gain insights with comprehensive reporting, performance metrics, and customer satisfaction tracking."
              }
            ].map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="card hover:shadow-lg transition-all duration-300 group">
                  <div className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white p-3 rounded-lg w-fit mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Our Core Values
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              The principles that guide everything we do
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[
              {
                title: "Customer Success First",
                description: "Every decision we make is guided by how it will impact our customers' success. We measure our success by your success."
              },
              {
                title: "Innovation & Excellence",
                description: "We continuously push boundaries to deliver cutting-edge solutions while maintaining the highest standards of quality."
              },
              {
                title: "Transparency & Trust",
                description: "We believe in open communication, honest feedback, and building lasting relationships based on trust and reliability."
              },
              {
                title: "Continuous Learning",
                description: "We embrace change, learn from feedback, and constantly evolve to meet the changing needs of our customers."
              }
            ].map((value, index) => (
              <div key={index} className="flex items-start space-x-4 p-6 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 hover:shadow-md transition-shadow duration-300">
                <div className="bg-blue-600 text-white p-2 rounded-lg flex-shrink-0">
                  <CheckCircle className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{value.title}</h3>
                  <p className="text-gray-700">{value.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Get In Touch
            </h2>
            <p className="text-xl opacity-90 max-w-2xl mx-auto">
              Have questions about OmniDesk? We'd love to hear from you.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            {[
              {
                icon: Mail,
                title: "Email Us",
                info: "support@omnidesk.com",
                description: "Get in touch via email"
              },
              {
                icon: Phone,
                title: "Call Us",
                info: "+1 (555) 123-4567",
                description: "Speak with our team"
              },
              {
                icon: MapPin,
                title: "Visit Us",
                info: "123 Tech Street, Silicon Valley",
                description: "Our headquarters"
              }
            ].map((contact, index) => {
              const Icon = contact.icon;
              return (
                <div key={index} className="bg-white/10 backdrop-blur-sm rounded-xl p-6 hover:bg-white/20 transition-colors duration-300">
                  <div className="bg-white/20 p-3 rounded-lg w-fit mx-auto mb-4">
                    <Icon className="h-8 w-8" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{contact.title}</h3>
                  <p className="text-lg font-medium mb-1">{contact.info}</p>
                  <p className="opacity-80">{contact.description}</p>
                </div>
              );
            })}
          </div>
          
          <div className="text-center mt-12">
            <Link 
              to="/client/submit" 
              className="inline-flex items-center bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors duration-200 shadow-lg"
            >
              <Ticket className="mr-2 h-5 w-5" />
              Submit a Support Ticket
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;

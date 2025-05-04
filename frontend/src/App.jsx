// Using React + Tailwind CSS for rapid development
function App() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-8 py-4 border-b">
        <div className="text-2xl font-bold">Student Advisor</div>
        <div className="flex gap-4">
          <button className="px-4 py-2">Documentation</button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded">Get Started</button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="grid grid-cols-2 gap-12 px-8 py-16">
        <div>
          <h1 className="text-5xl font-bold mb-6">
            Course recommendations
            <span className="text-blue-600"> powered by AI</span>
          </h1>
          <p className="text-gray-600 text-xl mb-8">
            Upload your transcript and job description to get personalized course recommendations.
          </p>
          <div className="flex gap-4">
            <button className="px-6 py-3 bg-blue-600 text-white rounded">
              Upload Transcript
            </button>
            <button className="px-6 py-3 border border-gray-300 rounded">
              Learn More
            </button>
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-8">
          {/* Form components will go here */}
        </div>
      </main>
    </div>
  )
}

export default App;

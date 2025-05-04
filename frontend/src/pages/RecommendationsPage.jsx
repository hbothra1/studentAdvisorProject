import React, { useState } from 'react';

function RecommendationsPage() {
  const [quarters, setQuarters] = useState([
    { id: 1, name: 'Fall 2023', courses: [] }
  ]);
  const [recommendations, setRecommendations] = useState(null);

  const addQuarter = () => {
    const newQuarter = {
      id: quarters.length + 1,
      name: `Quarter ${quarters.length + 1}`,
      courses: []
    };
    setQuarters([...quarters, newQuarter]);
  };

  const addCourse = (quarterId) => {
    const updatedQuarters = quarters.map(quarter => {
      if (quarter.id === quarterId) {
        return {
          ...quarter,
          courses: [...quarter.courses, { id: Date.now(), name: '', grade: '' }]
        };
      }
      return quarter;
    });
    setQuarters(updatedQuarters);
  };

  return (
    <div className="min-h-screen bg-white">
      <nav className="flex items-center justify-between px-8 py-4 border-b">
        <div className="text-2xl font-bold">Student Advisor</div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-12 grid grid-cols-2 gap-8">
        {/* Recommendations Section */}
        <section className="space-y-6">
          <h2 className="text-2xl font-bold mb-4">Your Recommendations</h2>
          <div className="bg-white rounded-lg shadow-sm border p-6">
            {recommendations ? (
              <div className="space-y-4">
                {/* Render recommendations here */}
              </div>
            ) : (
              <p className="text-gray-500">Loading recommendations...</p>
            )}
          </div>
        </section>

        {/* Course Input Section */}
        <section className="space-y-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Your Courses</h2>
            <button
              onClick={addQuarter}
              className="px-4 py-2 text-blue-600 border border-blue-600 rounded-lg"
            >
              Add Quarter
            </button>
          </div>

          {quarters.map(quarter => (
            <div key={quarter.id} className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-medium">{quarter.name}</h3>
                <button
                  onClick={() => addCourse(quarter.id)}
                  className="text-sm text-blue-600"
                >
                  + Add Course
                </button>
              </div>

              {quarter.courses.map(course => (
                <div key={course.id} className="grid grid-cols-2 gap-4 mb-4">
                  <input
                    type="text"
                    placeholder="Course Name"
                    className="p-2 border rounded"
                  />
                  <input
                    type="text"
                    placeholder="Grade"
                    className="p-2 border rounded"
                  />
                </div>
              ))}
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}

export default RecommendationsPage;

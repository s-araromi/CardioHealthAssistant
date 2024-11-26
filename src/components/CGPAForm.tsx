import React, { useState } from 'react';
import { PlusCircle, Trash2, Sparkles, Target } from 'lucide-react';

interface Course {
  id: string;
  name: string;
  grade: string;
  credits: number;
}

interface Prediction {
  predictedCGPA: number;
  recommendations: string[];
  targetAchievable: boolean;
}

export function CGPAForm() {
  const [scale, setScale] = useState<'4.0' | '5.0' | '7.0'>('4.0');
  const [courses, setCourses] = useState<Course[]>([
    { id: '1', name: '', grade: '', credits: 3 },
  ]);
  const [cgpa, setCGPA] = useState<number | null>(null);
  const [targetCGPA, setTargetCGPA] = useState<string>('');
  const [prediction, setPrediction] = useState<Prediction | null>(null);

  const gradePoints = {
    '4.0': { 'A+': 4.0, 'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7, 'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D': 1.0, 'F': 0 },
    '5.0': { 'A+': 5.0, 'A': 4.5, 'B': 4.0, 'C': 3.5, 'D': 3.0, 'E': 2.0, 'F': 0 },
    '7.0': { 'O': 7.0, 'A+': 6.0, 'A': 5.0, 'B+': 4.0, 'B': 3.0, 'C': 2.0, 'F': 0 },
  };

  // Course difficulty patterns (simplified AI simulation)
  const courseDifficulty = {
    'calculus': 0.8,
    'physics': 0.75,
    'programming': 0.7,
    'history': 0.6,
    'literature': 0.65,
    'chemistry': 0.75,
    'biology': 0.7,
    'economics': 0.65,
  };

  const addCourse = () => {
    setCourses([...courses, { id: Date.now().toString(), name: '', grade: '', credits: 3 }]);
  };

  const removeCourse = (id: string) => {
    setCourses(courses.filter(course => course.id !== id));
  };

  const updateCourse = (id: string, field: keyof Course, value: string | number) => {
    setCourses(courses.map(course => 
      course.id === id ? { ...course, [field]: value } : course
    ));
  };

  const calculateCGPA = () => {
    let totalPoints = 0;
    let totalCredits = 0;

    courses.forEach(course => {
      if (course.grade && course.credits) {
        const points = gradePoints[scale][course.grade as keyof typeof gradePoints['4.0']];
        totalPoints += points * course.credits;
        totalCredits += course.credits;
      }
    });

    if (totalCredits === 0) return;
    const calculated = Number((totalPoints / totalCredits).toFixed(2));
    setCGPA(calculated);
    return calculated;
  };

  const predictFutureCGPA = () => {
    const currentCGPA = calculateCGPA();
    if (!currentCGPA || !targetCGPA) return;

    const target = parseFloat(targetCGPA);
    const coursePatterns = courses.map(course => {
      const lowercaseName = course.name.toLowerCase();
      let difficulty = 0.7; // default difficulty
      
      // Find matching difficulty patterns
      Object.entries(courseDifficulty).forEach(([key, value]) => {
        if (lowercaseName.includes(key)) {
          difficulty = value;
        }
      });
      
      return {
        name: course.name,
        difficulty,
        grade: course.grade,
      };
    });

    // Predict based on current performance and course patterns
    const averagePerformance = coursePatterns.reduce((acc, course) => {
      if (course.grade) {
        const gradeValue = gradePoints[scale][course.grade as keyof typeof gradePoints['4.0']];
        return acc + (gradeValue / parseFloat(scale) * course.difficulty);
      }
      return acc;
    }, 0) / coursePatterns.filter(c => c.grade).length;

    const predictedCGPA = Number((currentCGPA * 0.7 + averagePerformance * 0.3).toFixed(2));
    const targetAchievable = predictedCGPA >= target - 0.5;

    // Generate smart recommendations
    const recommendations = [];
    if (predictedCGPA < target) {
      if (coursePatterns.some(c => c.difficulty > 0.7)) {
        recommendations.push("Consider balancing difficult courses across semesters");
      }
      if (coursePatterns.filter(c => c.grade).length < 4) {
        recommendations.push("Take more courses to improve prediction accuracy");
      }
      recommendations.push(`Focus on courses with difficulty level ${(target / parseFloat(scale) * 0.7).toFixed(2)} or lower`);
    }

    setPrediction({
      predictedCGPA,
      recommendations,
      targetAchievable,
    });
  };

  return (
    <div className="space-y-6">
      {/* Scale Selection */}
      <div className="flex gap-4 justify-center mb-6">
        {(['4.0', '5.0', '7.0'] as const).map((s) => (
          <button
            key={s}
            onClick={() => setScale(s)}
            className={`px-4 py-2 rounded-lg transition-all ${
              scale === s
                ? 'bg-indigo-600 text-white shadow-lg'
                : 'bg-white/50 hover:bg-white text-gray-600'
            }`}
          >
            {s} Scale
          </button>
        ))}
      </div>

      {/* Target CGPA Input */}
      <div className="flex gap-4 items-center bg-white/50 p-4 rounded-lg">
        <Target className="w-5 h-5 text-indigo-600" />
        <input
          type="number"
          step="0.01"
          placeholder="Set your target CGPA"
          value={targetCGPA}
          onChange={(e) => setTargetCGPA(e.target.value)}
          className="flex-1 px-4 py-2 rounded-lg bg-white/50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Column Headers */}
      <div className="grid grid-cols-[1fr,120px,100px,48px] gap-4 mb-2 px-1">
        <div className="text-sm font-medium text-gray-700">Course Name</div>
        <div className="text-sm font-medium text-gray-700">Grade</div>
        <div className="text-sm font-medium text-gray-700">Course Unit</div>
        <div></div>
      </div>

      {/* Course List */}
      <div className="space-y-4">
        {courses.map((course) => (
          <div key={course.id} className="grid grid-cols-[1fr,120px,100px,48px] gap-4 items-center animate-fadeIn">
            <input
              type="text"
              placeholder="Enter course name"
              value={course.name}
              onChange={(e) => updateCourse(course.id, 'name', e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-white/50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <select
              value={course.grade}
              onChange={(e) => updateCourse(course.id, 'grade', e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-white/50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Select</option>
              {Object.keys(gradePoints[scale]).map((grade) => (
                <option key={grade} value={grade}>
                  {grade}
                </option>
              ))}
            </select>
            <input
              type="number"
              min="0"
              max="6"
              value={course.credits}
              onChange={(e) => updateCourse(course.id, 'credits', parseInt(e.target.value) || 0)}
              className="w-full px-4 py-2 rounded-lg bg-white/50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              onClick={() => removeCourse(course.id)}
              className="p-2 text-red-500 hover:text-red-600 transition-colors"
              aria-label="Remove course"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="flex justify-between items-center pt-4">
        <button
          onClick={addCourse}
          className="flex items-center gap-2 px-4 py-2 text-indigo-600 hover:text-indigo-700 transition-colors"
        >
          <PlusCircle className="w-5 h-5" />
          Add Course
        </button>
        <div className="flex gap-2">
          <button
            onClick={calculateCGPA}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Calculate CGPA
          </button>
          <button
            onClick={predictFutureCGPA}
            className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            Predict
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="space-y-4">
        {cgpa !== null && (
          <div className="p-4 bg-white rounded-lg shadow-lg text-center animate-fadeIn">
            <h3 className="text-lg font-semibold text-gray-700">Current CGPA</h3>
            <p className="text-3xl font-bold text-indigo-600">{cgpa}</p>
          </div>
        )}

        {prediction && (
          <div className="p-6 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg shadow-lg animate-fadeIn">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-purple-600" />
              <h3 className="text-lg font-semibold text-gray-700">AI Predictions</h3>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-white rounded-lg">
                <span className="text-gray-600">Predicted CGPA</span>
                <span className="text-xl font-bold text-purple-600">{prediction.predictedCGPA}</span>
              </div>
              
              <div className="p-4 bg-white rounded-lg">
                <h4 className="font-medium text-gray-700 mb-2">Target Analysis</h4>
                <div className={`text-sm ${prediction.targetAchievable ? 'text-green-600' : 'text-amber-600'}`}>
                  {prediction.targetAchievable 
                    ? "✨ Your target CGPA appears achievable!"
                    : "⚠️ Reaching your target CGPA may be challenging"}
                </div>
              </div>

              {prediction.recommendations.length > 0 && (
                <div className="p-4 bg-white rounded-lg">
                  <h4 className="font-medium text-gray-700 mb-2">Recommendations</h4>
                  <ul className="space-y-2">
                    {prediction.recommendations.map((rec, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-purple-600">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
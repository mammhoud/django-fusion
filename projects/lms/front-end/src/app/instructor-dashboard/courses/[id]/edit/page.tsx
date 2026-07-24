'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { HiArrowLeft, HiPlus, HiTrash, HiPhotograph, HiChevronUp, HiChevronDown, HiSave } from 'react-icons/hi';

interface Lesson {
  id: string;
  title: string;
  duration: string;
  videoUrl: string;
}

interface Module {
  id: string;
  title: string;
  lessons: Lesson[];
}

const mockCourse = {
  id: '1',
  title: 'Advanced React Development',
  category: 'Development',
  level: 'Advanced',
  price: 89.99,
  description: 'Master React with advanced patterns, performance optimization, and real-world project experience.',
  thumbnail: 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800',
  modules: [
    {
      id: 'm1',
      title: 'React Fundamentals Review',
      lessons: [
        { id: 'l1', title: 'Component Architecture', duration: '15:30', videoUrl: '' },
        { id: 'l2', title: 'State Management Patterns', duration: '22:00', videoUrl: '' },
      ],
    },
    {
      id: 'm2',
      title: 'Performance Optimization',
      lessons: [
        { id: 'l3', title: 'React.memo & useMemo', duration: '18:45', videoUrl: '' },
        { id: 'l4', title: 'Code Splitting Strategies', duration: '25:15', videoUrl: '' },
      ],
    },
  ],
};

export default function EditCoursePage() {
  const params = useParams();
  const router = useRouter();
  const courseId = params?.id?.[0] || '';
  const isNew = !courseId || courseId === 'new';

  const [title, setTitle] = useState(isNew ? '' : mockCourse.title);
  const [category, setCategory] = useState(isNew ? '' : mockCourse.category);
  const [level, setLevel] = useState(isNew ? '' : mockCourse.level);
  const [price, setPrice] = useState(isNew ? '' : String(mockCourse.price));
  const [description, setDescription] = useState(isNew ? '' : mockCourse.description);
  const [modules, setModules] = useState<Module[]>(isNew ? [] : mockCourse.modules);
  const [saving, setSaving] = useState(false);

  const addModule = () => {
    const newModule: Module = {
      id: `m${Date.now()}`,
      title: '',
      lessons: [],
    };
    setModules([...modules, newModule]);
  };

  const addLesson = (moduleId: string) => {
    setModules(modules.map((m) =>
      m.id === moduleId
        ? { ...m, lessons: [...m.lessons, { id: `l${Date.now()}`, title: '', duration: '', videoUrl: '' }] }
        : m
    ));
  };

  const handleSave = async () => {
    setSaving(true);
    // Simulate API call
    await new Promise((r) => setTimeout(r, 1500));
    setSaving(false);
    router.push('/instructor-dashboard/courses');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link href="/instructor-dashboard/courses" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-indigo-600 mb-2 transition-colors">
              <HiArrowLeft className="w-4 h-4" />
              Back to Courses
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">{isNew ? 'Create New Course' : 'Edit Course'}</h1>
          </div>
          <button
            onClick={handleSave}
            disabled={saving}
            className="btn-primary flex items-center gap-2"
          >
            <HiSave className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save Course'}
          </button>
        </div>

        <div className="space-y-8">
          {/* Basic Info */}
          <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Course Title</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="e.g., Advanced React Development"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                >
                  <option value="">Select category</option>
                  <option value="Development">Development</option>
                  <option value="Design">Design</option>
                  <option value="Business">Business</option>
                  <option value="Marketing">Marketing</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Level</label>
                <select
                  value={level}
                  onChange={(e) => setLevel(e.target.value)}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                >
                  <option value="">Select level</option>
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Price ($)</label>
                <input
                  type="number"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="0.00"
                  min="0"
                  step="0.01"
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none resize-none"
                placeholder="Describe your course..."
              />
            </div>
          </section>

          {/* Thumbnail */}
          <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Course Thumbnail</h2>
            <div className="flex items-center gap-6">
              <div className="w-40 h-24 bg-gray-100 rounded-xl flex items-center justify-center overflow-hidden">
                {mockCourse.thumbnail ? (
                  <img src={mockCourse.thumbnail} alt="" className="w-full h-full object-cover" />
                ) : (
                  <HiPhotograph className="w-8 h-8 text-gray-400" />
                )}
              </div>
              <button className="px-4 py-2 text-sm border border-gray-200 rounded-xl text-gray-600 hover:bg-gray-50 transition-colors">
                Upload Image
              </button>
            </div>
          </section>

          {/* Curriculum */}
          <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Curriculum</h2>
              <button onClick={addModule} className="btn-secondary text-sm flex items-center gap-1">
                <HiPlus className="w-4 h-4" />
                Add Module
              </button>
            </div>

            <div className="space-y-4">
              {modules.map((mod, modIdx) => (
                <div key={mod.id} className="border border-gray-200 rounded-xl overflow-hidden">
                  <div className="flex items-center gap-3 p-4 bg-gray-50">
                    <HiChevronUp className="w-4 h-4 text-gray-400 cursor-move" />
                    <input
                      type="text"
                      value={mod.title}
                      onChange={(e) => {
                        const updated = [...modules];
                        updated[modIdx] = { ...updated[modIdx], title: e.target.value };
                        setModules(updated);
                      }}
                      className="flex-1 px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                      placeholder="Module title"
                    />
                    <button
                      onClick={() => addLesson(mod.id)}
                      className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
                    >
                      + Add Lesson
                    </button>
                    <button
                      onClick={() => setModules(modules.filter((m) => m.id !== mod.id))}
                      className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                    >
                      <HiTrash className="w-4 h-4" />
                    </button>
                  </div>

                  {mod.lessons.map((lesson, lessIdx) => (
                    <div key={lesson.id} className="flex items-center gap-3 px-4 py-3 border-t border-gray-100">
                      <HiChevronDown className="w-3 h-3 text-gray-300" />
                      <input
                        type="text"
                        value={lesson.title}
                        onChange={(e) => {
                          const updated = [...modules];
                          updated[modIdx] = {
                            ...updated[modIdx],
                            lessons: updated[modIdx].lessons.map((l, i) =>
                              i === lessIdx ? { ...l, title: e.target.value } : l
                            ),
                          };
                          setModules(updated);
                        }}
                        className="flex-1 px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                        placeholder="Lesson title"
                      />
                      <input
                        type="text"
                        value={lesson.duration}
                        onChange={(e) => {
                          const updated = [...modules];
                          updated[modIdx] = {
                            ...updated[modIdx],
                            lessons: updated[modIdx].lessons.map((l, i) =>
                              i === lessIdx ? { ...l, duration: e.target.value } : l
                            ),
                          };
                          setModules(updated);
                        }}
                        className="w-20 px-2 py-1.5 border border-gray-200 rounded-lg text-sm text-center focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                        placeholder="0:00"
                      />
                      <button className="p-1 text-gray-400 hover:text-indigo-600 transition-colors">
                        <HiPhotograph className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => {
                          const updated = [...modules];
                          updated[modIdx] = {
                            ...updated[modIdx],
                            lessons: updated[modIdx].lessons.filter((_, i) => i !== lessIdx),
                          };
                          setModules(updated);
                        }}
                        className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                      >
                        <HiTrash className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              ))}

              {modules.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                  <p className="text-sm">No modules yet. Click &quot;Add Module&quot; to start building your curriculum.</p>
                </div>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

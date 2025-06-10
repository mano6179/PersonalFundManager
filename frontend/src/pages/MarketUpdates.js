import React, { useState, useEffect } from 'react';
import { marketUpdatesAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-toastify';

const MarketUpdates = () => {
    const [updates, setUpdates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { user } = useAuth();

    useEffect(() => {
        fetchUpdates();
    }, []);

    const fetchUpdates = async () => {
        try {
            setLoading(true);
            const response = await marketUpdatesAPI.getUpdates();
            setUpdates(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to fetch market updates');
            toast.error('Failed to fetch market updates');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateUpdate = async (updateData) => {
        try {
            const response = await marketUpdatesAPI.createUpdate({
                ...updateData,
                author: user.name,
                timestamp: new Date().toISOString()
            });
            setUpdates(prev => [response.data, ...prev]);
            toast.success('Market update created successfully');
        } catch (err) {
            toast.error('Failed to create market update');
        }
    };

    const handleUpdateUpdate = async (id, updateData) => {
        try {
            const response = await marketUpdatesAPI.updateUpdate(id, updateData);
            setUpdates(prev => 
                prev.map(update => 
                    update.id === id ? response.data : update
                )
            );
            toast.success('Market update updated successfully');
        } catch (err) {
            toast.error('Failed to update market update');
        }
    };

    const handleDeleteUpdate = async (id) => {
        try {
            await marketUpdatesAPI.deleteUpdate(id);
            setUpdates(prev => prev.filter(update => update.id !== id));
            toast.success('Market update deleted successfully');
        } catch (err) {
            toast.error('Failed to delete market update');
        }
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold mb-6">Market Updates</h1>
            
            {/* Create Update Form */}
            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Create New Update</h2>
                <form onSubmit={(e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    handleCreateUpdate({
                        title: formData.get('title'),
                        content: formData.get('content'),
                        category: formData.get('category'),
                        is_public: formData.get('is_public') === 'true',
                        tags: formData.get('tags').split(',').map(tag => tag.trim())
                    });
                    e.target.reset();
                }}>
                    <div className="grid grid-cols-1 gap-4">
                        <input
                            type="text"
                            name="title"
                            placeholder="Title"
                            className="border p-2 rounded"
                            required
                        />
                        <textarea
                            name="content"
                            placeholder="Content"
                            className="border p-2 rounded"
                            required
                        />
                        <select
                            name="category"
                            className="border p-2 rounded"
                            required
                        >
                            <option value="">Select Category</option>
                            <option value="Technical">Technical</option>
                            <option value="Fundamental">Fundamental</option>
                            <option value="News">News</option>
                        </select>
                        <select
                            name="is_public"
                            className="border p-2 rounded"
                            required
                        >
                            <option value="true">Public</option>
                            <option value="false">Private</option>
                        </select>
                        <input
                            type="text"
                            name="tags"
                            placeholder="Tags (comma-separated)"
                            className="border p-2 rounded"
                        />
                        <button
                            type="submit"
                            className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
                        >
                            Create Update
                        </button>
                    </div>
                </form>
            </div>

            {/* Updates List */}
            <div className="space-y-4">
                {updates.map(update => (
                    <div key={update.id} className="border p-4 rounded">
                        <div className="flex justify-between items-start">
                            <div>
                                <h3 className="text-lg font-semibold">{update.title}</h3>
                                <p className="text-gray-600">{update.content}</p>
                                <div className="mt-2">
                                    <span className="bg-gray-200 px-2 py-1 rounded text-sm">
                                        {update.category}
                                    </span>
                                    {update.is_public && (
                                        <span className="bg-green-200 px-2 py-1 rounded text-sm ml-2">
                                            Public
                                        </span>
                                    )}
                                </div>
                                <div className="mt-2">
                                    {update.tags.map(tag => (
                                        <span
                                            key={tag}
                                            className="bg-blue-200 px-2 py-1 rounded text-sm mr-2"
                                        >
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                            <div className="flex space-x-2">
                                <button
                                    onClick={() => handleUpdateUpdate(update.id, {
                                        ...update,
                                        is_public: !update.is_public
                                    })}
                                    className="text-blue-500 hover:text-blue-700"
                                >
                                    Toggle Public
                                </button>
                                <button
                                    onClick={() => handleDeleteUpdate(update.id)}
                                    className="text-red-500 hover:text-red-700"
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                        <div className="mt-2 text-sm text-gray-500">
                            By {update.author} on {new Date(update.timestamp).toLocaleString()}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MarketUpdates;

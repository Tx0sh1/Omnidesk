import React, { useState, useEffect } from 'react';
import { 
  MessageCircle, 
  Send, 
  Edit2, 
  Trash2, 
  Eye, 
  EyeOff, 
  Clock, 
  User,
  AlertCircle,
  CheckCircle,
  MoreVertical
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface Comment {
  id: number;
  content: string;
  created_at: string;
  updated_at?: string;
  is_internal: boolean;
  time_ago: string;
  author: {
    id: number;
    username: string;
  };
}

interface CommentListProps {
  ticketId: number;
  onCommentAdded?: () => void;
}

const CommentList: React.FC<CommentListProps> = ({ ticketId, onCommentAdded }) => {
  const { user } = useAuth();
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newComment, setNewComment] = useState('');
  const [isInternal, setIsInternal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editContent, setEditContent] = useState('');
  const [editIsInternal, setEditIsInternal] = useState(false);

  useEffect(() => {
    fetchComments();
  }, [ticketId]);

  const fetchComments = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch(`/api/tickets/${ticketId}/comments`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setComments(data.comments || []);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to load comments');
      }
    } catch (err) {
      setError('Failed to load comments');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitComment = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newComment.trim()) return;

    try {
      setSubmitting(true);
      
      const response = await fetch(`/api/tickets/${ticketId}/comments`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: newComment.trim(),
          is_internal: isInternal
        })
      });

      if (response.ok) {
        const data = await response.json();
        setComments([...comments, data.comment]);
        setNewComment('');
        setIsInternal(false);
        if (onCommentAdded) {
          onCommentAdded();
        }
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to add comment');
      }
    } catch (err) {
      setError('Failed to add comment');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditComment = async (commentId: number) => {
    if (!editContent.trim()) return;

    try {
      const response = await fetch(`/api/comments/${commentId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: editContent.trim(),
          is_internal: editIsInternal
        })
      });

      if (response.ok) {
        const data = await response.json();
        setComments(comments.map(c => c.id === commentId ? data.comment : c));
        setEditingId(null);
        setEditContent('');
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to update comment');
      }
    } catch (err) {
      setError('Failed to update comment');
    }
  };

  const handleDeleteComment = async (commentId: number) => {
    if (!confirm('Are you sure you want to delete this comment?')) return;

    try {
      const response = await fetch(`/api/comments/${commentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        setComments(comments.filter(c => c.id !== commentId));
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to delete comment');
      }
    } catch (err) {
      setError('Failed to delete comment');
    }
  };

  const startEdit = (comment: Comment) => {
    setEditingId(comment.id);
    setEditContent(comment.content);
    setEditIsInternal(comment.is_internal);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditContent('');
    setEditIsInternal(false);
  };

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading comments...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Comments Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <MessageCircle className="h-5 w-5 mr-2 text-blue-500" />
          Comments ({comments.length})
        </h3>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-sm text-red-600">{error}</span>
            <button
              onClick={() => setError('')}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Comments List */}
      <div className="space-y-4">
        {comments.length === 0 ? (
          <div className="text-center py-8">
            <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No comments yet</p>
            <p className="text-sm text-gray-500">Be the first to add a comment</p>
          </div>
        ) : (
          comments.map((comment) => (
            <div
              key={comment.id}
              className={`card relative ${
                comment.is_internal ? 'bg-yellow-50 border-yellow-200' : 'bg-white'
              }`}
            >
              {/* Internal Comment Badge */}
              {comment.is_internal && (
                <div className="absolute top-3 right-3">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                    <EyeOff className="h-3 w-3 mr-1" />
                    Internal
                  </span>
                </div>
              )}

              <div className="flex items-start space-x-3">
                {/* Avatar */}
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <User className="h-4 w-4 text-blue-600" />
                  </div>
                </div>

                {/* Comment Content */}
                <div className="flex-1 min-w-0">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-gray-900">
                        {comment.author.username}
                      </span>
                      <span className="text-sm text-gray-500 flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {comment.time_ago}
                      </span>
                      {comment.updated_at && (
                        <span className="text-xs text-gray-400">(edited)</span>
                      )}
                    </div>

                    {/* Actions */}
                    {(user?.is_admin || comment.author.id === user?.id) && (
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => startEdit(comment)}
                          className="p-1 text-gray-400 hover:text-gray-600 rounded"
                          title="Edit comment"
                        >
                          <Edit2 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteComment(comment.id)}
                          className="p-1 text-gray-400 hover:text-red-600 rounded"
                          title="Delete comment"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Content */}
                  {editingId === comment.id ? (
                    <div className="space-y-3">
                      <textarea
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                        className="form-input w-full"
                        rows={3}
                        placeholder="Edit your comment..."
                      />
                      
                      {(user?.is_admin) && (
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={editIsInternal}
                            onChange={(e) => setEditIsInternal(e.target.checked)}
                            className="form-checkbox"
                          />
                          <span className="ml-2 text-sm text-gray-700">Internal comment</span>
                        </label>
                      )}

                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleEditComment(comment.id)}
                          className="btn btn-sm btn-primary"
                          disabled={!editContent.trim()}
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Save
                        </button>
                        <button
                          onClick={cancelEdit}
                          className="btn btn-sm btn-secondary"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="prose prose-sm max-w-none text-gray-700">
                      <p className="whitespace-pre-wrap">{comment.content}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Comment Form */}
      <div className="card">
        <form onSubmit={handleSubmitComment} className="space-y-4">
          <div>
            <label className="form-label">Add Comment</label>
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              className="form-input"
              rows={4}
              placeholder="Type your comment here..."
              disabled={submitting}
            />
          </div>

          {user?.is_admin && (
            <div className="flex items-center">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={isInternal}
                  onChange={(e) => setIsInternal(e.target.checked)}
                  className="form-checkbox"
                  disabled={submitting}
                />
                <span className="ml-2 text-sm text-gray-700">Internal comment (only visible to staff)</span>
              </label>
            </div>
          )}

          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500">
              {isInternal ? (
                <span className="flex items-center text-yellow-600">
                  <EyeOff className="h-4 w-4 mr-1" />
                  This comment will be internal only
                </span>
              ) : (
                <span className="flex items-center text-green-600">
                  <Eye className="h-4 w-4 mr-1" />
                  This comment will be visible to the client
                </span>
              )}
            </p>

            <button
              type="submit"
              className="btn btn-primary flex items-center space-x-2"
              disabled={!newComment.trim() || submitting}
            >
              {submitting ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Send className="h-4 w-4" />
              )}
              <span>{submitting ? 'Adding...' : 'Add Comment'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CommentList;

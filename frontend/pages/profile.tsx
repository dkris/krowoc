import { useAuth } from '../lib/AuthContext';
import ProtectedRoute from '../components/auth/ProtectedRoute';

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <ProtectedRoute>
      <div className="py-8">
        <div className="max-w-3xl mx-auto bg-white shadow rounded-lg overflow-hidden">
          <div className="px-6 py-8">
            <h2 className="text-2xl font-bold mb-6">Profile</h2>
            
            {user && (
              <div className="space-y-4">
                <div className="border-b pb-4">
                  <p className="text-sm text-gray-500 mb-1">Email</p>
                  <p className="font-medium">{user.email}</p>
                </div>
                
                <div className="border-b pb-4">
                  <p className="text-sm text-gray-500 mb-1">User ID</p>
                  <p className="font-medium">{user.id}</p>
                </div>
                
                {user.user_metadata && (
                  <div className="border-b pb-4">
                    <p className="text-sm text-gray-500 mb-1">Full Name</p>
                    <p className="font-medium">
                      {user.user_metadata.full_name || 'Not provided'}
                    </p>
                  </div>
                )}
                
                <div className="border-b pb-4">
                  <p className="text-sm text-gray-500 mb-1">Last Sign In</p>
                  <p className="font-medium">
                    {user.last_sign_in_at 
                      ? new Date(user.last_sign_in_at).toLocaleString() 
                      : 'Never'}
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500 mb-1">Provider</p>
                  <p className="font-medium capitalize">
                    {user.app_metadata?.provider || 'email'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
} 
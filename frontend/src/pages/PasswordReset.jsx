import React from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";
import { useToast } from "../hooks/use-toast";
import { apiPasswordResetRequest, apiPasswordResetConfirm } from "../lib/api";

export default function PasswordResetPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const token = searchParams.get('token');

  if (token) {
    return <PasswordResetConfirm token={token} />;
  } else {
    return <PasswordResetRequest />;
  }
}

function PasswordResetRequest() {
  const { toast } = useToast();
  const [email, setEmail] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [sent, setSent] = React.useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) return;

    try {
      setLoading(true);
      await apiPasswordResetRequest({ email });
      setSent(true);
      toast({
        title: "Reset link sent!",
        description: "Check your email for password reset instructions."
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error?.response?.data?.detail || "Failed to send reset email. Please try again."
      });
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-rose-50 to-pink-50">
        <div className="pt-8 pb-4 text-center">
          <Link to="/" className="text-2xl font-bold text-rose-600 hover:text-rose-700">
            The giftspace
          </Link>
          <p className="text-gray-600 mt-2">Password Reset</p>
        </div>
        
        <div className="flex items-center justify-center px-4">
          <Card className="w-full max-w-md shadow-lg">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl font-semibold">Check Your Email</CardTitle>
            </CardHeader>
            <CardContent className="text-center space-y-4">
              <p className="text-gray-600">
                We've sent password reset instructions to <strong>{email}</strong>
              </p>
              <p className="text-sm text-gray-500">
                Check your email and click the reset link to create a new password.
                The link will expire in 1 hour.
              </p>
              <div className="space-y-2">
                <Button onClick={() => setSent(false)} variant="outline" className="w-full">
                  Send another email
                </Button>
                <Link to="/auth" className="block">
                  <Button variant="secondary" className="w-full">
                    Back to Sign In
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 to-pink-50">
      <div className="pt-8 pb-4 text-center">
        <Link to="/" className="text-2xl font-bold text-rose-600 hover:text-rose-700">
          The giftspace
        </Link>
        <p className="text-gray-600 mt-2">Reset Your Password</p>
      </div>
      
      <div className="flex items-center justify-center px-4">
        <Card className="w-full max-w-md shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-semibold">Forgot Password?</CardTitle>
            <p className="text-gray-600 mt-2">Enter your email to receive reset instructions</p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label>Email Address</Label>
                <Input 
                  type="email" 
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)} 
                  placeholder="Enter your email address"
                  required 
                />
              </div>
              <Button type="submit" disabled={loading} className="w-full">
                {loading ? "Sending..." : "Send Reset Link"}
              </Button>
            </form>
            
            <div className="text-center mt-6">
              <Link to="/auth" className="text-sm text-muted-foreground underline">
                Back to Sign In
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function PasswordResetConfirm({ token }) {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [password, setPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [loading, setLoading] = React.useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      toast({
        title: "Password mismatch",
        description: "Please make sure your passwords match."
      });
      return;
    }

    if (password.length < 8) {
      toast({
        title: "Password too short",
        description: "Password must be at least 8 characters long."
      });
      return;
    }

    try {
      setLoading(true);
      await apiPasswordResetConfirm({ token, new_password: password });
      
      toast({
        title: "Password reset successful!",
        description: "You can now sign in with your new password."
      });
      
      navigate("/auth");
    } catch (error) {
      toast({
        title: "Reset failed",
        description: error?.response?.data?.detail || "Invalid or expired reset token. Please request a new one."
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 to-pink-50">
      <div className="pt-8 pb-4 text-center">
        <Link to="/" className="text-2xl font-bold text-rose-600 hover:text-rose-700">
          The giftspace
        </Link>
        <p className="text-gray-600 mt-2">Reset Your Password</p>
      </div>
      
      <div className="flex items-center justify-center px-4">
        <Card className="w-full max-w-md shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-semibold">Create New Password</CardTitle>
            <p className="text-gray-600 mt-2">Enter your new password below</p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label>New Password</Label>
                <Input 
                  type="password" 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                  placeholder="Enter new password (min 8 characters)"
                  required 
                  minLength={8}
                />
              </div>
              <div>
                <Label>Confirm Password</Label>
                <Input 
                  type="password" 
                  value={confirmPassword} 
                  onChange={(e) => setConfirmPassword(e.target.value)} 
                  placeholder="Confirm new password"
                  required 
                />
              </div>
              <Button type="submit" disabled={loading} className="w-full">
                {loading ? "Updating..." : "Update Password"}
              </Button>
            </form>
            
            <div className="text-center mt-6">
              <Link to="/auth" className="text-sm text-muted-foreground underline">
                Back to Sign In
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
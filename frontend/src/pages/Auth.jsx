import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";
import { useAuth } from "../context/AuthContext";
import { useNavigate, Link } from "react-router-dom";
import { useToast } from "../hooks/use-toast";
import { PROFESSIONAL_COPY } from "../utils/professionalCopy";

export default function AuthPage() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [loading, setLoading] = React.useState(false);

  const onLogin = async ({ email, password }) => {
    try {
      setLoading(true);
      await login(email, password);
      navigate("/dashboard");
      toast({ 
        title: "Welcome back!", 
        description: "Successfully signed in to your account." 
      });
    } catch (e) {
      toast({ 
        title: "Sign in failed", 
        description: e?.response?.data?.detail || "Please check your credentials and try again." 
      });
    } finally {
      setLoading(false);
    }
  };

  const onSignup = async ({ name, email, password }) => {
    try {
      setLoading(true);
      await register(name, email, password);
      navigate("/dashboard");
      toast({ 
        title: "Welcome to The giftspace!", 
        description: "Your account has been created successfully." 
      });
    } catch (e) {
      toast({ 
        title: "Registration failed", 
        description: e?.response?.data?.detail || "Please check your information and try again." 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 to-pink-50">
      {/* Header */}
      <div className="pt-8 pb-4 text-center">
        <Link to="/" className="text-2xl font-bold text-rose-600 hover:text-rose-700">
          The giftspace
        </Link>
        <p className="text-gray-600 mt-2">Your perfect wedding registry platform</p>
      </div>
      
      <div className="flex items-center justify-center px-4 pb-16">
        <Card className="w-full max-w-md shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-semibold">Get Started</CardTitle>
            <p className="text-gray-600 mt-2">Create your beautiful wedding registry in minutes</p>
          </CardHeader>
        <CardContent>
          <Tabs defaultValue="login">
            <TabsList className="grid grid-cols-2 w-full">
              <TabsTrigger value="login">Sign in</TabsTrigger>
              <TabsTrigger value="signup">Sign up</TabsTrigger>
            </TabsList>
            <TabsContent value="login" className="mt-4">
              <LoginForm onLogin={onLogin} loading={loading} />
            </TabsContent>
            <TabsContent value="signup" className="mt-4">
              <SignupForm onSignup={onSignup} loading={loading} />
            </TabsContent>
          </Tabs>
          <div className="text-center mt-6 text-sm text-muted-foreground">
            <Link className="underline" to="/">Back to home</Link>
          </div>
        </CardContent>
        </Card>
      </div>
    </div>
  );
}

function LoginForm({ onLogin, loading }) {
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onLogin({ email, password });
      }}
      className="space-y-3"
      data-testid="login-form"
    >
      <div>
        <Label>Email</Label>
        <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </div>
      <div>
        <Label>Password</Label>
        <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      </div>
      <Button aria-label="Log in" type="submit" disabled={loading} className="w-full mt-2" data-testid="login-submit">
        {loading ? "Please wait…" : "Log in"}
      </Button>
    </form>
  );
}

function SignupForm({ onSignup, loading }) {
  const [name, setName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSignup({ name, email, password });
      }}
      className="space-y-3"
      data-testid="signup-form"
    >
      <div>
        <Label>Full name</Label>
        <Input value={name} onChange={(e) => setName(e.target.value)} required />
      </div>
      <div>
        <Label>Email</Label>
        <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </div>
      <div>
        <Label>Password</Label>
        <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      </div>
      <Button aria-label="Create account" type="submit" disabled={loading} className="w-full mt-2" data-testid="signup-submit">
        {loading ? "Please wait…" : "Create account"}
      </Button>
    </form>
  );
}
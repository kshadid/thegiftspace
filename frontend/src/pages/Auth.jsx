import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";
import { useAuth } from "../context/AuthContext";
import { useNavigate, Link } from "react-router-dom";
import { useToast } from "../hooks/use-toast";

export default function AuthPage() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [loading, setLoading] = React.useState(false);

  const onLogin = async ({ email, password }) => {
    try {
      setLoading(true);
      await login(email, password);
      navigate("/create");
    } catch (e) {
      toast({ title: "Login failed", description: e?.response?.data?.detail || e?.message || "Please try again." });
    } finally {
      setLoading(false);
    }
  };

  const onSignup = async ({ name, email, password }) => {
    try {
      setLoading(true);
      await register(name, email, password);
      navigate("/create");
    } catch (e) {
      toast({ title: "Signup failed", description: e?.response?.data?.detail || e?.message || "Please try again." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-16">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">Welcome</CardTitle>
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
  );
}

function LoginForm({ onLogin, loading }) {
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  return (
    <div className="space-y-3">
      <div>
        <Label>Email</Label>
        <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </div>
      <div>
        <Label>Password</Label>
        <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      </div>
      <Button type="button" disabled={loading} className="w-full mt-2" onClick={() => onLogin({ email, password })}>
        {loading ? "Please wait…" : "Log in"}
      </Button>
    </div>
  );
}

function SignupForm({ onSignup, loading }) {
  const [name, setName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  return (
    <div className="space-y-3">
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
      <Button type="button" disabled={loading} className="w-full mt-2" onClick={() => onSignup({ name, email, password })}>
        {loading ? "Please wait…" : "Create account"}
      </Button>
    </div>
  );
}
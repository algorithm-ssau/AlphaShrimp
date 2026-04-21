import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
// import { Button } from '@/components/ui/button';
// import { Input } from '@/components/ui/input';
// import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function AuthPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useAuth();

    const handleAuth = async (type: 'login' | 'register') => {
        const res = await fetch(`/api/auth/${type}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });
        const data = await res.json();
        if (data.token) login(data.token, data.user);
        else alert(data.error);
    };

    return (<div>AuthPage</div>) // (
        // <div className="flex items-center justify-center min-h-screen bg-zinc-50">
        //     <Card className="w-full max-w-sm">
        //         <CardHeader><CardTitle className="text-center">AlphaShrimp</CardTitle></CardHeader>
        //         <CardContent>
        //             <Tabs defaultValue="login">
        //                 <TabsList className="grid w-full grid-cols-2"><TabsTrigger value="login">Login</TabsTrigger><TabsTrigger value="register">Register</TabsTrigger></TabsList>
        //                 <div className="mt-4 space-y-4">
        //                     <Input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        //                     <Input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
        //                     <TabsContent value="login"><Button className="w-full" onClick={() => handleAuth('login')}>Login</Button></TabsContent>
        //                     <TabsContent value="register"><Button className="w-full" onClick={() => handleAuth('register')}>Register</Button></TabsContent>
        //                 </div>
        //             </Tabs>
        //         </CardContent>
        //     </Card>
        // </div>
    // );
}
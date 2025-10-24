import { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import { Trash2, CheckCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminPanel() {
  const [authenticated, setAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState({
    title: '',
    description: '',
    location: '',
    date: '',
    image: ''
  });

  useEffect(() => {
    const token = localStorage.getItem('adminToken');
    if (token) {
      setAuthenticated(true);
      fetchItems();
    }
  }, []);

  const handleLogin = async () => {
    try {
      const res = await axios.post(`${API}/admin/login`, { password });
      localStorage.setItem('adminToken', res.data.token);
      setAuthenticated(true);
      toast.success('Login realizado!');
      fetchItems();
    } catch (err) {
      toast.error('Senha incorreta');
    }
  };

  const fetchItems = async () => {
    try {
      const res = await axios.get(`${API}/feed`);
      setItems(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setNewItem({ ...newItem, image: reader.result });
      };
      reader.readAsDataURL(file);
    }
  };

  const createItem = async () => {
    if (!newItem.title || !newItem.image || !newItem.location || !newItem.date) {
      toast.error('Preencha todos os campos');
      return;
    }
    try {
      await axios.post(`${API}/items`, newItem);
      toast.success('Item criado!');
      setNewItem({ title: '', description: '', location: '', date: '', image: '' });
      fetchItems();
    } catch (err) {
      toast.error('Erro ao criar item');
    }
  };

  const deleteItem = async (id) => {
    try {
      await axios.delete(`${API}/items/${id}`);
      toast.success('Item removido');
      fetchItems();
    } catch (err) {
      toast.error('Erro ao remover item');
    }
  };

  const resolveItem = async (id) => {
    try {
      await axios.put(`${API}/items/${id}/resolve`);
      toast.success('Item marcado como resolvido');
      fetchItems();
    } catch (err) {
      toast.error('Erro ao resolver item');
    }
  };

  if (!authenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#6B28C8] to-[#9b59d0] flex items-center justify-center p-4">
        <Card className="w-full max-w-md p-8 space-y-6">
          <h1 className="text-3xl font-bold text-center">Admin Login</h1>
          <Input
            data-testid="admin-password-input"
            type="password"
            placeholder="Senha de administrador"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
          />
          <Button data-testid="admin-login-btn" onClick={handleLogin} className="w-full bg-[#FF9500] hover:bg-[#e08600] text-white rounded-full py-6 text-lg font-semibold">
            Entrar
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-[#6B28C8] text-white py-4 px-4 shadow-lg">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">Painel Admin</h1>
          <div className="flex gap-3">
            <a href="/" className="text-sm underline">Ver Feed</a>
            <button
              data-testid="admin-logout-btn"
              onClick={() => {
                localStorage.removeItem('adminToken');
                setAuthenticated(false);
              }}
              className="text-sm underline"
            >
              Sair
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        <Card className="p-6 space-y-4">
          <h2 className="text-2xl font-bold">Criar Novo Item</h2>
          <Input
            data-testid="admin-title-input"
            placeholder="Título do item"
            value={newItem.title}
            onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
          />
          <Textarea
            data-testid="admin-description-input"
            placeholder="Descrição"
            value={newItem.description}
            onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
            rows={3}
          />
          <Input
            data-testid="admin-location-input"
            placeholder="Local encontrado"
            value={newItem.location}
            onChange={(e) => setNewItem({ ...newItem, location: e.target.value })}
          />
          <Input
            data-testid="admin-date-input"
            type="date"
            value={newItem.date}
            onChange={(e) => setNewItem({ ...newItem, date: e.target.value })}
          />
          <Input data-testid="admin-image-input" type="file" accept="image/*" onChange={handleImageUpload} />
          {newItem.image && <img src={newItem.image} alt="Preview" className="w-32 h-32 object-cover rounded-lg" />}
          <Button data-testid="admin-create-btn" onClick={createItem} className="w-full bg-[#FF9500] hover:bg-[#e08600] text-white rounded-full py-6 text-lg font-semibold">
            Criar Item
          </Button>
        </Card>

        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Itens Cadastrados</h2>
          {items.map((item) => (
            <Card key={item.id} data-testid={`admin-item-${item.id}`} className="p-6 space-y-4">
              <div className="flex gap-4">
                <img src={item.image} alt={item.title} className="w-24 h-24 object-cover rounded-lg" />
                <div className="flex-1">
                  <h3 className="text-lg font-bold">{item.title}</h3>
                  <p className="text-sm text-gray-600">{item.location} • {item.date}</p>
                  <p className="text-sm text-gray-700">{item.description}</p>
                  {item.claimed && <p className="text-[#FF9500] font-semibold mt-2">✓ Reclamado por {item.claims.length} pessoa(s)</p>}
                  {item.resolved && <p className="text-green-600 font-semibold">✓ Resolvido</p>}
                </div>
              </div>
              <div className="flex gap-3">
                <Button
                  data-testid={`admin-resolve-btn-${item.id}`}
                  onClick={() => resolveItem(item.id)}
                  disabled={item.resolved}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                >
                  <CheckCircle className="mr-2" size={18} />
                  Resolver
                </Button>
                <Button
                  data-testid={`admin-delete-btn-${item.id}`}
                  onClick={() => deleteItem(item.id)}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                >
                  <Trash2 className="mr-2" size={18} />
                  Remover
                </Button>
              </div>
              {item.claims.length > 0 && (
                <div className="mt-4 space-y-2">
                  <h4 className="font-semibold">Reclamações:</h4>
                  {item.claims.map((claim) => (
                    <div key={claim.id} className="bg-gray-50 p-3 rounded-lg">
                      <p className="text-sm font-semibold">{claim.name}</p>
                      <p className="text-sm text-gray-600">Contato: {claim.contact}</p>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}
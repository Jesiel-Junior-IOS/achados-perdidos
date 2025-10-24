import { useState, useEffect } from 'react';
import axios from 'axios';
import { MessageCircle, Package } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Feed() {
  const [items, setItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [commentModal, setCommentModal] = useState(false);
  const [claimModal, setClaimModal] = useState(false);
  const [commentForm, setCommentForm] = useState({ name: '', text: '' });
  const [claimForm, setClaimForm] = useState({ name: '', contact: '' });

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const res = await axios.get(`${API}/feed`);
      setItems(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const openComments = (item) => {
    setSelectedItem(item);
    setCommentModal(true);
  };

  const openClaim = (item) => {
    setSelectedItem(item);
    setClaimModal(true);
  };

  const submitComment = async () => {
    if (!commentForm.name || !commentForm.text) {
      toast.error('Preencha todos os campos');
      return;
    }
    try {
      await axios.post(`${API}/items/${selectedItem.id}/comment`, commentForm);
      toast.success('Comentário adicionado!');
      setCommentForm({ name: '', text: '' });
      setCommentModal(false);
      fetchItems();
    } catch (err) {
      toast.error('Erro ao adicionar comentário');
    }
  };

  const submitClaim = async () => {
    if (!claimForm.name || !claimForm.contact) {
      toast.error('Preencha todos os campos');
      return;
    }
    try {
      await axios.post(`${API}/items/${selectedItem.id}/claim`, claimForm);
      toast.success('Item reclamado com sucesso!');
      setClaimForm({ name: '', contact: '' });
      setClaimModal(false);
      fetchItems();
    } catch (err) {
      toast.error('Erro ao reclamar item');
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <header className="sticky top-0 z-50 bg-[#6B28C8] text-white py-4 px-4 shadow-lg">
        <div className="max-w-2xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">Achados e Perdidos</h1>
          <a href="/admin" className="text-sm underline">Admin</a>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {items.length === 0 && (
          <p className="text-center text-gray-500 py-12">Nenhum item perdido ainda</p>
        )}
        {items.map((item) => (
          <div key={item.id} data-testid={`item-card-${item.id}`} className="bg-white rounded-3xl shadow-lg overflow-hidden border border-gray-100">
            <img src={item.image} alt={item.title} className="w-full h-80 object-cover" />
            <div className="p-5 space-y-3">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-bold text-gray-800">{item.title}</h2>
                  <p className="text-sm text-gray-600">{item.location} • {item.date}</p>
                </div>
                {item.claimed && (
                  <span className="bg-[#FF9500] text-white text-xs px-3 py-1 rounded-full font-semibold">Reclamado</span>
                )}
              </div>
              <p className="text-gray-700">{item.description}</p>
              
              <div className="flex gap-3">
                <Button
                  data-testid={`comment-btn-${item.id}`}
                  onClick={() => openComments(item)}
                  className="flex-1 bg-[#6B28C8] hover:bg-[#5a20a8] text-white rounded-full py-6 text-base font-semibold transition-all"
                >
                  <MessageCircle className="mr-2" size={20} />
                  Comentar ({item.comments.length})
                </Button>
                <Button
                  data-testid={`claim-btn-${item.id}`}
                  onClick={() => openClaim(item)}
                  disabled={item.claimed}
                  className="flex-1 bg-[#FF9500] hover:bg-[#e08600] text-white rounded-full py-6 text-base font-semibold transition-all disabled:opacity-50"
                >
                  <Package className="mr-2" size={20} />
                  É meu item
                </Button>
              </div>

              {item.comments.length > 0 && (
                <div className="mt-4 space-y-2">
                  {item.comments.slice(-3).map((comment) => (
                    <div key={comment.id} className="bg-gray-50 rounded-2xl p-3">
                      <p className="text-sm font-semibold text-gray-800">{comment.name}</p>
                      <p className="text-sm text-gray-600">{comment.text}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </main>

      <Dialog open={commentModal} onOpenChange={setCommentModal}>
        <DialogContent data-testid="comment-modal" className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Adicionar Comentário</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <Input
              data-testid="comment-name-input"
              placeholder="Seu nome"
              value={commentForm.name}
              onChange={(e) => setCommentForm({ ...commentForm, name: e.target.value })}
            />
            <Textarea
              data-testid="comment-text-input"
              placeholder="Seu comentário"
              value={commentForm.text}
              onChange={(e) => setCommentForm({ ...commentForm, text: e.target.value })}
              rows={4}
            />
            <Button data-testid="comment-submit-btn" onClick={submitComment} className="w-full bg-[#6B28C8] hover:bg-[#5a20a8] text-white rounded-full py-6">
              Enviar Comentário
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={claimModal} onOpenChange={setClaimModal}>
        <DialogContent data-testid="claim-modal" className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Reclamar Item</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <Input
              data-testid="claim-name-input"
              placeholder="Seu nome"
              value={claimForm.name}
              onChange={(e) => setClaimForm({ ...claimForm, name: e.target.value })}
            />
            <Input
              data-testid="claim-contact-input"
              placeholder="WhatsApp ou contato"
              value={claimForm.contact}
              onChange={(e) => setClaimForm({ ...claimForm, contact: e.target.value })}
            />
            <Button data-testid="claim-submit-btn" onClick={submitClaim} className="w-full bg-[#FF9500] hover:bg-[#e08600] text-white rounded-full py-6">
              Confirmar Reclamação
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
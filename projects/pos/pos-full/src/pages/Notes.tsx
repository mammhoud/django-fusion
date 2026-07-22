import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { MdNoteAdd, MdEdit, MdDelete, MdDrafts, MdSave, MdRestore, MdArchive, MdClose, MdSearch } from 'react-icons/md';
import { FaStickyNote, FaSave, FaPlus, FaTrash, FaUndo } from 'react-icons/fa';
import PageLayout from '../components/PageLayout';
import { useTranslation } from 'react-i18next';
import {
  useGetNotesQuery,
  useAddNoteMutation,
  useUpdateNoteMutation,
  useDeleteNoteMutation,
  type Note,
} from '../store/api/endpoints/notes';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import StatusToast from '../components/StatusToast';

type NoteStatus = 'draft' | 'saved' | 'archived';
type RefType = '' | 'cart' | 'inventory' | 'count' | 'order' | 'customer';

const REF_TYPE_ICONS: Record<RefType, string> = {
  '': '📝',
  cart: '🛒',
  inventory: '📦',
  count: '🔢',
  order: '📋',
  customer: '👤',
};

const STATUS_COLORS: Record<NoteStatus, string> = {
  draft: 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400 border-yellow-300 dark:border-yellow-700',
  saved: 'bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-300 dark:border-green-700',
  archived: 'bg-slate-100 dark:bg-slate-800/30 text-slate-500 dark:text-slate-400 border-slate-300 dark:border-slate-600',
};

export default function Notes() {
  const { t } = useTranslation();
  const [showDrafts, setShowDrafts] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Editor state
  const [editorOpen, setEditorOpen] = useState(false);
  const [editNote, setEditNote] = useState<Note | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [status, setStatus] = useState<NoteStatus>('draft');
  const [refType, setRefType] = useState<RefType>('');
  const [refId, setRefId] = useState('');

  // Delete confirmation
  const [deleteTarget, setDeleteTarget] = useState<Note | null>(null);

  // Toast
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // ── RTK Query ──
  const { data: allNotes, isLoading } = useGetNotesQuery({});
  const [addNote] = useAddNoteMutation();
  const [updateNote] = useUpdateNoteMutation();
  const [deleteNote] = useDeleteNoteMutation();

  // Filter notes
  const notes = Array.isArray(allNotes) ? allNotes : [];
  const drafts = notes.filter((n) => n.status === 'draft');
  const savedNotes = notes.filter((n) => n.status === 'saved');

  const filteredNotes = (showDrafts ? drafts : savedNotes).filter((n) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      n.title.toLowerCase().includes(q) ||
      n.content.toLowerCase().includes(q)
    );
  });

  const showStatus = (type: 'success' | 'error', msg: string) => {
    setToast({ type, message: msg });
    setTimeout(() => setToast(null), 3000);
  };

  // ── Open editor for new or edit ──
  const openNew = () => {
    setEditNote(null);
    setTitle('');
    setContent('');
    setStatus('draft');
    setRefType('');
    setRefId('');
    setEditorOpen(true);
  };

  const openEdit = (note: Note) => {
    setEditNote(note);
    setTitle(note.title);
    setContent(note.content);
    setStatus(note.status as NoteStatus);
    setRefType((note.reference_type || '') as RefType);
    setRefId(note.reference_id ? String(note.reference_id) : '');
    setEditorOpen(true);
  };

  const restoreDraft = (note: Note) => {
    openEdit(note);
  };

  // ── Save / Update ──
  const handleSave = async () => {
    if (!content.trim() && !title.trim()) {
      showStatus('error', 'Title or content is required');
      return;
    }
    try {
      const payload: Partial<Note> = {
        title: title.trim(),
        content: content.trim(),
        status,
        reference_type: refType || '',
        reference_id: refId ? Number(refId) : null,
      };

      if (editNote) {
        await updateNote({ id: editNote.id, data: payload }).unwrap();
        showStatus('success', 'Note updated');
      } else {
        await addNote(payload).unwrap();
        showStatus('success', 'Note saved');
      }
      setEditorOpen(false);
    } catch (e) {
      showStatus('error', String(e));
    }
  };

  // ── Delete ──
  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteNote(deleteTarget.id).unwrap();
      setDeleteTarget(null);
      showStatus('success', 'Note deleted');
    } catch (e) {
      showStatus('error', String(e));
    }
  };

  // ── Restore draft → saved ──
  const handleSaveDraft = async (note: Note) => {
    try {
      await updateNote({ id: note.id, data: { status: 'saved' } }).unwrap();
      showStatus('success', 'Draft saved');
    } catch (e) {
      showStatus('error', String(e));
    }
  };

  // ── Archive / Un-archive ──
  const handleArchive = async (note: Note) => {
    try {
      await updateNote({ id: note.id, data: { status: note.status === 'archived' ? 'saved' : 'archived' } }).unwrap();
      showStatus('success', note.status === 'archived' ? 'Note restored' : 'Note archived');
    } catch (e) {
      showStatus('error', String(e));
    }
  };

  return (
    <PageLayout
      title={<><FaStickyNote className="text-amber-500" /> Notes</>}
      background="bg-linear-to-br from-slate-100 via-amber-50 to-slate-100 dark:from-slate-900 dark:via-amber-950 dark:to-slate-900"
    >
      {/* ── Toolbar ── */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-6">
        <div className="flex items-center gap-2">
          <motion.button
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            onClick={() => setShowDrafts(true)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              showDrafts
                ? 'bg-amber-500 text-white shadow-lg'
                : 'bg-white/70 dark:bg-white/10 text-slate-700 dark:text-gray-300'
            }`}
          >
            <MdDrafts /> Drafts ({drafts.length})
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            onClick={() => setShowDrafts(false)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              !showDrafts
                ? 'bg-green-500 text-white shadow-lg'
                : 'bg-white/70 dark:bg-white/10 text-slate-700 dark:text-gray-300'
            }`}
          >
            <MdSave /> Saved ({savedNotes.length})
          </motion.button>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-56">
            <MdSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search notes…"
              className="w-full pl-9 pr-3 py-1.5 rounded-lg text-xs bg-white/50 dark:bg-white/5
                border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white
                placeholder:text-slate-400 focus:outline-none focus:border-amber-400 transition-colors"
            />
          </div>
          <motion.button
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            onClick={openNew}
            className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-white rounded-xl font-semibold text-sm shrink-0"
          >
            <FaPlus /> New Note
          </motion.button>
        </div>
      </div>

      {/* ── Note Grid ── */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card--glass rounded-xl p-5 animate-pulse">
              <div className="h-5 bg-slate-200 dark:bg-white/10 rounded w-2/3 mb-3" />
              <div className="h-4 bg-slate-200 dark:bg-white/10 rounded w-full mb-2" />
              <div className="h-4 bg-slate-200 dark:bg-white/10 rounded w-4/5 mb-4" />
              <div className="h-3 bg-slate-200 dark:bg-white/10 rounded w-1/3" />
            </div>
          ))}
        </div>
      ) : filteredNotes.length === 0 ? (
        <div className="text-center py-16">
          <FaStickyNote className="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
          <p className="text-lg text-slate-500 dark:text-white/50 mb-1">
            {showDrafts ? 'No drafts yet' : 'No saved notes yet'}
          </p>
          <p className="text-sm text-slate-400 dark:text-white/30 mb-4">
            {showDrafts
              ? 'Create a new note — it starts as a draft'
              : 'Save drafts to store them permanently'}
          </p>
          <motion.button
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            onClick={openNew}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-amber-500 text-white rounded-xl font-semibold text-sm"
          >
            <MdNoteAdd className="w-5 h-5" /> Write your first note
          </motion.button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {filteredNotes.map((note) => (
              <motion.div
                key={note.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className={`card--glass rounded-xl p-5 border-l-4 transition-all hover:shadow-md ${
                  note.status === 'draft'
                    ? 'border-l-amber-400'
                    : note.status === 'archived'
                    ? 'border-l-slate-400 opacity-70'
                    : 'border-l-green-400'
                }`}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-slate-900 dark:text-white truncate">
                      {note.title || 'Untitled'}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium border ${STATUS_COLORS[note.status as NoteStatus] || STATUS_COLORS.saved}`}>
                        {note.status}
                      </span>
                      {note.reference_type && (
                        <span className="text-[10px] text-slate-400 dark:text-slate-500">
                          {REF_TYPE_ICONS[note.reference_type as RefType] || '📝'} {note.reference_type}
                          {note.reference_id ? ` #${note.reference_id}` : ''}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-1 ml-2 shrink-0">
                    {note.status === 'draft' && (
                      <button
                        onClick={() => handleSaveDraft(note)}
                        className="text-green-500 hover:text-green-400 p-1.5 rounded-lg hover:bg-green-500/10"
                        title="Save draft"
                      >
                        <FaSave className="w-3.5 h-3.5" />
                      </button>
                    )}
                    <button
                      onClick={() => openEdit(note)}
                      className="text-blue-500 hover:text-blue-400 p-1.5 rounded-lg hover:bg-blue-500/10"
                      title="Edit"
                    >
                      <MdEdit className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleArchive(note)}
                      className="text-slate-500 hover:text-slate-400 p-1.5 rounded-lg hover:bg-slate-500/10"
                      title={note.status === 'archived' ? 'Restore' : 'Archive'}
                    >
                      {note.status === 'archived' ? <FaUndo className="w-3.5 h-3.5" /> : <MdArchive className="w-3.5 h-3.5" />}
                    </button>
                    <button
                      onClick={() => setDeleteTarget(note)}
                      className="text-red-500 hover:text-red-400 p-1.5 rounded-lg hover:bg-red-500/10"
                      title="Delete"
                    >
                      <FaTrash className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                {/* Content preview */}
                <p className="text-sm text-slate-600 dark:text-gray-400 whitespace-pre-wrap line-clamp-4 mb-3">
                  {note.content || '…'}
                </p>

                {/* Footer — date + restore button for drafts */}
                <div className="flex items-center justify-between text-[10px] text-slate-400 dark:text-slate-500">
                  <span>{new Date(note.updated_at).toLocaleDateString()}</span>
                  {note.status === 'draft' && (
                    <button
                      onClick={() => restoreDraft(note)}
                      className="flex items-center gap-1 text-amber-500 hover:text-amber-400 font-medium"
                    >
                      <MdRestore className="w-3 h-3" /> Restore
                    </button>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* ── Editor Modal ── */}
      <Modal
        isOpen={editorOpen}
        onClose={() => setEditorOpen(false)}
        title={editNote ? 'Edit Note' : 'New Note'}
        size="lg"
        footer={
          <>
            <button
              onClick={() => setEditorOpen(false)}
              className="flex-1 py-2.5 rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white font-semibold hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="flex-1 py-2.5 rounded-lg bg-amber-500 text-white font-semibold flex items-center justify-center gap-2 hover:bg-amber-600 transition-colors"
            >
              <FaSave /> {editNote ? 'Update' : 'Save'}
            </button>
          </>
        }
      >
        <div className="space-y-4">
          {/* Title */}
          <div>
            <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm font-medium">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Note title (optional)"
              className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-sm"
            />
          </div>

          {/* Content */}
          <div>
            <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm font-medium">Content</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Write your note here…"
              rows={6}
              className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-sm resize-y"
            />
          </div>

          {/* Status & Reference */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm font-medium">Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as NoteStatus)}
                className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-sm"
              >
                <option value="draft">Draft</option>
                <option value="saved">Saved</option>
                <option value="archived">Archived</option>
              </select>
            </div>
            <div>
              <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm font-medium">Reference Type</label>
              <select
                value={refType}
                onChange={(e) => setRefType(e.target.value as RefType)}
                className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-sm"
              >
                <option value="">General</option>
                <option value="cart">Cart</option>
                <option value="inventory">Inventory</option>
                <option value="count">Count</option>
                <option value="order">Order</option>
                <option value="customer">Customer</option>
              </select>
            </div>
            <div>
              <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm font-medium">Reference ID</label>
              <input
                type="number"
                value={refId}
                onChange={(e) => setRefId(e.target.value)}
                placeholder="Optional entity ID"
                className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-sm"
              />
            </div>
          </div>
        </div>
      </Modal>

      {/* ── Delete Confirm ── */}
      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete Note"
        message="Are you sure you want to delete this note? This cannot be undone."
        itemName={deleteTarget?.title || 'Untitled'}
      />

      <StatusToast type={toast?.type || 'success'} message={toast?.message || ''} visible={!!toast} onDismiss={() => setToast(null)} />
    </PageLayout>
  );
}

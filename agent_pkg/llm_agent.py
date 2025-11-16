import re
import torch
import torch.nn as nn
import torch.nn.functional as F
from utils.helpers import log_event


#Simple Tokenizer
class SimpleTokenizer:
    def __init__(self, unk_token="<unk>", pad_token="<pad>", bos_token="<bos>", eos_token="<eos>"):
        self.unk_token = unk_token
        self.pad_token = pad_token
        self.bos_token = bos_token
        self.eos_token = eos_token
        self.token_to_id = {
            pad_token: 0,
            bos_token: 1,
            eos_token: 2,
            unk_token: 3,
        }
        self.id_to_token = {i: t for t, i in self.token_to_id.items()}

    def build_vocab(self, texts):
        for t in texts:
            for tok in self._basic_tokenize(t):
                if tok not in self.token_to_id:
                    idx = len(self.token_to_id)
                    self.token_to_id[tok] = idx
                    self.id_to_token[idx] = tok

    def _basic_tokenize(self, text):
        text = text.lower().strip()
        return re.findall(r"[a-z0-9\-]+|[^\s]", text)

    def encode(self, text, add_special=True):
        toks = self._basic_tokenize(text)
        ids = [self.token_to_id.get(tok, self.token_to_id[self.unk_token]) for tok in toks]
        if add_special:
            ids = [self.token_to_id[self.bos_token]] + ids + [self.token_to_id[self.eos_token]]
        return ids

    def decode(self, ids):
        toks = [self.id_to_token.get(i, self.unk_token) for i in ids]
        toks = [t for t in toks if t not in {self.bos_token, self.eos_token, self.pad_token}]
        return " ".join(toks)

    @property
    def vocab_size(self):
        return len(self.token_to_id)


# RNN Language Model
class RNNLM(nn.Module):
    def __init__(self, vocab_size, emb_dim=64, hidden_dim=128):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, emb_dim)
        self.rnn = nn.GRU(emb_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x, hidden=None):
        x = self.embed(x)
        out, hidden = self.rnn(x, hidden)
        logits = self.fc(out)
        return logits, hidden

    @torch.no_grad()
    def generate(self, start_ids, max_new_tokens=50, temperature=1.0):
        hidden = None
        ids = start_ids.clone()
        for _ in range(max_new_tokens):
            logits, hidden = self.forward(ids[:, -1:], hidden)
            probs = F.softmax(logits[:, -1] / temperature, dim=-1)
            next_id = torch.multinomial(probs, num_samples=1)
            ids = torch.cat([ids, next_id], dim=1)
        return ids


# Local LLM Wrapper
class LocalLLM:
    def __init__(self, model, tokenizer, device=None):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def generate(self, prompt: str, max_new_tokens=50):
        ids = torch.tensor([self.tokenizer.encode(prompt)], dtype=torch.long, device=self.device)
        out_ids = self.model.generate(ids, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(out_ids[0].tolist())


# Agent Class
class LLMAgent:
    def __init__(self, name: str, llm, model_name="local-llm"):
        self.name = name
        self.llm = llm
        self.model = model_name
        self.perceived_data = None
        self.response = None

    def perceive(self, data: dict):
        self.perceived_data = data
        log_event({"agent": self.name, "event": "perceive", "data": data})

    def decide(self, prompt: str):
        text = self.llm.generate(prompt)
        self.response = text
        log_event({"agent": self.name, "event": "decide", "response": self.response})
        return self.response

    def act(self):
        log_event({"agent": self.name, "event": "act", "results": self.response})
        return self.response


if __name__ == "__main__":
    texts = [
        "ERP system pending approval",
        "Warehouse picked items",
        "Invoice matched against PO"
    ]
    tokenizer = SimpleTokenizer()
    tokenizer.build_vocab(texts)

    model = RNNLM(vocab_size=tokenizer.vocab_size)
    llm = LocalLLM(model, tokenizer)

    agent = LLMAgent(name="ERP-Assistant", llm=llm)
    agent.perceive({"context": "ERP ops"})
    print(agent.decide("Summarize procurement bottlenecks"))
    print(agent.act())
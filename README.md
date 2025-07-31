# 🔐 AES-128 over FHE (CKKS)  
**2025 Summer Internship – PACLAB | Team 2**

## 📦 Environment  
- Library: [Desilo Liberate.FHE](https://fhe.desilo.dev/latest/)  
- Standard: [NIST FIPS 197 – Advanced Encryption Standard (AES)](https://doi.org/10.6028/NIST.FIPS.197-upd1)

## 📁 File Structure
```
├── he_aes.py         # AES implementation using HE
├── he_context.py     # DesiloFHE engine setup and utility 
├── he_lut.py         # LUT (Look-Up Table) based operations
├── plain_aes.py      # Standard AES implementation for comparison
├── interface.py      # Handles user inputs and CLI interaction
├── main.py           # Controls the overall execution flow
```

## 📊 Weekly Slides
- [Week 1](https://docs.google.com/presentation/d/17Go-Mh1oqvs5DQHm751l8px0L2x1tEgaoQTtfMuRHDw/edit?usp=sharing)
- [Week 2](https://docs.google.com/presentation/d/1Q_aoKzQZD8EI7Ii7wgfAUFP40EdUkUxcW8TnQ-nWsw8/edit?usp=sharing)
- [Week 3](https://docs.google.com/presentation/d/18WOduYhY1kZ5We5Qbxn-jG6F0ogmIAsb-vXh-uSEro8/edit?usp=sharing)
- [Week 4](https://docs.google.com/presentation/d/1MlLkRWqBk5yzXDRcRN9YMjVbloJCHoNg7J1JkGICp0k/edit?usp=sharing)
  
## 🧾 References  

- Homomorphic Evaluation of the AES Circuit (Updated Implementation)  
   [https://eprint.iacr.org/2012/099](https://eprint.iacr.org/2012/099)

- At Last! A Homomorphic AES Evaluation in Less than 30 Seconds by Means of TFHE  
   [https://eprint.iacr.org/2023/1020](https://eprint.iacr.org/2023/1020)

- **Amortized Large Look-up Table Evaluation with Multivariate Polynomials for Homomorphic Encryption**  
   [https://eprint.iacr.org/2024/274](https://eprint.iacr.org/2024/274)

## ⚙️ GitHub Guide  

*Please customize the parameters according to your needs*

- **First setup**:  
  `git clone`

- **Sync with main branch**:  
  `git checkout main`, `git pull origin main`  
  or
  `git fetch origin`, `git merge origin/main`

- **(Before work) Create / Switch branch**:  
  `git checkout`

- **(After modification) Stage changes**:  
  `git add`

- **Commit**:  
  `git commit`

- **Push to remote**:  
  `git push`

- **Pull request & Merge**:  
  Create a pull request (PR) on GitHub, then review and merge it


# Local Imports 
from   backend.models    import Profile, Banco
from   backend.functions import Functions

p = Profile(nome="CSRG LTDA",cnpj='46811890000112',bancos=[])

if __name__ == "__main__":
    
    main = Functions(p)
    
    while True:
        main.run()
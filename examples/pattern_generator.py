file_path = "./file.bin"

with open(file_path, "wb") as file:
    for j in range(0, 2):    
        for i in range(0, 256):
            my_bytes = i.to_bytes(1, byteorder='big')
            file.write(my_bytes)
        for i in range(0, 256):
            my_bytes = (255-i).to_bytes(1, byteorder='big')
            file.write(my_bytes)
file.close()
